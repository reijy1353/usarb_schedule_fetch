from raw_schedule_data_fetch import get_raw_schedule_json

# Parsing the 
def parse_raw_schedule_json(group_name: str, week: int = 1, debug: bool = False):
    # Get the RAW json
    r_lessons = get_raw_schedule_json(group_name, university_week=week, debug=debug)
    
if __name__ == "__main__":
    parse_raw_schedule_json("IT11Z", 10, debug=True)