"""
Schedule change detection module.
Compares old and new schedule data to detect changes.
"""
import json
import os
from datetime import date
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from raw_schedule_data_fetch import get_raw_schedule_json
from data_parser import generate_event_id, calc_university_week_from_date


@dataclass
class ScheduleChange:
    """Represents a change in the schedule."""
    type: str  # 'added', 'removed', 'modified'
    week: int
    day_number: int
    lesson_number: int
    old_lesson: Optional[Dict] = None
    new_lesson: Optional[Dict] = None
    event_id: Optional[str] = None


class ScheduleMonitor:
    """Monitor schedule changes and detect differences."""
    
    def __init__(self, snapshot_file: str = "schedule_snapshot.json"):
        self.snapshot_file = snapshot_file
        self.snapshot: Dict = {}
        self._load_snapshot()
    
    def _load_snapshot(self):
        """Load the last known schedule snapshot."""
        if os.path.exists(self.snapshot_file):
            try:
                with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                    self.snapshot = json.load(f)
            except Exception as e:
                print(f"Error loading snapshot: {e}")
                self.snapshot = {}
        else:
            self.snapshot = {}
    
    def _save_snapshot(self):
        """Save the current schedule snapshot."""
        try:
            with open(self.snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(self.snapshot, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving snapshot: {e}")
    
    def _normalize_lesson(self, lesson: Dict, group_name: str, week: int) -> Dict:
        """Normalize lesson data for comparison."""
        return {
            'event_id': generate_event_id(
                group_name, week,
                lesson.get('day_number', 0),
                lesson.get('cours_nr', 0),
                lesson.get('cours_name', ''),
                lesson.get('cours_type', '')
            ),
            'day_number': lesson.get('day_number', 0),
            'lesson_number': lesson.get('cours_nr', 0),
            'cours_name': lesson.get('cours_name', ''),
            'cours_type': lesson.get('cours_type', ''),
            'cours_office': lesson.get('cours_office', ''),
            'teacher_name': lesson.get('teacher_name', ''),
        }
    
    def fetch_current_schedule(self, group_name: str, weeks: List[int]) -> Dict:
        """Fetch current schedule for specified weeks."""
        current = {}
        for week in weeks:
            try:
                raw_data = get_raw_schedule_json(group_name, university_week=week)
                entries = raw_data.get("week") or []
                
                # Normalize and index by event_id
                week_key = str(week)
                current[week_key] = {}
                
                for lesson in entries:
                    normalized = self._normalize_lesson(lesson, group_name, week)
                    event_id = normalized['event_id']
                    current[week_key][event_id] = normalized
            except Exception as e:
                print(f"Error fetching week {week}: {e}")
                continue
        
        return current
    
    def detect_changes(
        self, 
        group_name: str, 
        weeks: List[int],
        current_schedule: Optional[Dict] = None
    ) -> List[ScheduleChange]:
        """
        Detect changes between saved snapshot and current schedule.
        
        Returns:
            List of ScheduleChange objects
        """
        if current_schedule is None:
            current_schedule = self.fetch_current_schedule(group_name, weeks)
        
        changes = []
        
        # Get saved schedule for these weeks
        saved_schedule = self.snapshot.get(group_name, {})
        
        for week in weeks:
            week_key = str(week)
            current_week = current_schedule.get(week_key, {})
            saved_week = saved_schedule.get(week_key, {})
            
            # Get sets of event IDs
            current_ids: Set[str] = set(current_week.keys())
            saved_ids: Set[str] = set(saved_week.keys())
            
            # Find added lessons
            added_ids = current_ids - saved_ids
            for event_id in added_ids:
                lesson = current_week[event_id]
                changes.append(ScheduleChange(
                    type='added',
                    week=week,
                    day_number=lesson['day_number'],
                    lesson_number=lesson['lesson_number'],
                    new_lesson=lesson,
                    event_id=event_id
                ))
            
            # Find removed lessons
            removed_ids = saved_ids - current_ids
            for event_id in removed_ids:
                lesson = saved_week[event_id]
                changes.append(ScheduleChange(
                    type='removed',
                    week=week,
                    day_number=lesson['day_number'],
                    lesson_number=lesson['lesson_number'],
                    old_lesson=lesson,
                    event_id=event_id
                ))
            
            # Find modified lessons (same event_id but different content)
            common_ids = current_ids & saved_ids
            for event_id in common_ids:
                current_lesson = current_week[event_id]
                saved_lesson = saved_week[event_id]
                
                # Compare key fields (ignore event_id itself)
                current_fields = {k: v for k, v in current_lesson.items() if k != 'event_id'}
                saved_fields = {k: v for k, v in saved_lesson.items() if k != 'event_id'}
                
                if current_fields != saved_fields:
                    changes.append(ScheduleChange(
                        type='modified',
                        week=week,
                        day_number=current_lesson['day_number'],
                        lesson_number=current_lesson['lesson_number'],
                        old_lesson=saved_lesson,
                        new_lesson=current_lesson,
                        event_id=event_id
                    ))
        
        return changes
    
    def update_snapshot(self, group_name: str, weeks: List[int], schedule: Optional[Dict] = None):
        """Update the saved snapshot with current schedule."""
        if schedule is None:
            schedule = self.fetch_current_schedule(group_name, weeks)
        
        if group_name not in self.snapshot:
            self.snapshot[group_name] = {}
        
        for week in weeks:
            week_key = str(week)
            self.snapshot[group_name][week_key] = schedule.get(week_key, {})
        
        self._save_snapshot()
    
    def format_changes(self, changes: List[ScheduleChange]) -> str:
        """Format changes for display."""
        if not changes:
            return "✅ No changes detected"
        
        lines = [f"📊 Found {len(changes)} change(s):\n"]
        
        # Group by type
        added = [c for c in changes if c.type == 'added']
        removed = [c for c in changes if c.type == 'removed']
        modified = [c for c in changes if c.type == 'modified']
        
        if added:
            lines.append(f"➕ Added ({len(added)}):")
            for change in added:
                lesson = change.new_lesson
                lines.append(f"  • Week {change.week}, Day {change.day_number}, Lesson {change.lesson_number}")
                lines.append(f"    {lesson['cours_name']} | {lesson['cours_type']}")
        
        if removed:
            lines.append(f"\n➖ Removed ({len(removed)}):")
            for change in removed:
                lesson = change.old_lesson
                lines.append(f"  • Week {change.week}, Day {change.day_number}, Lesson {change.lesson_number}")
                lines.append(f"    {lesson['cours_name']} | {lesson['cours_type']}")
        
        if modified:
            lines.append(f"\n✏️ Modified ({len(modified)}):")
            for change in modified:
                old_lesson = change.old_lesson
                new_lesson = change.new_lesson
                lines.append(f"  • Week {change.week}, Day {change.day_number}, Lesson {change.lesson_number}")
                lines.append(f"    {old_lesson['cours_name']} → {new_lesson['cours_name']}")
                
                # Show specific field changes
                fields_changed = []
                for key in ['cours_name', 'cours_type', 'cours_office', 'teacher_name']:
                    if old_lesson.get(key) != new_lesson.get(key):
                        fields_changed.append(f"{key}: {old_lesson.get(key)} → {new_lesson.get(key)}")
                
                if fields_changed:
                    lines.append(f"    Changes: {', '.join(fields_changed)}")
        
        return "\n".join(lines)

