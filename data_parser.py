
pass

from ast import parse
from raw_schedule_data_fetch import get_raw_schedule_data






if __name__ == "__main__":
    data = get_raw_schedule_data("IT11Z", university_week=11, debug=False)

    mapping = {        
        1: "monday",
        2: "tuesday",
        3: "wednesday",
        4: "thursday",
        5: "friday",
        6: "saturday",
    }
    
    parsed_data = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
    }
    
    for i in data["week"]:
        parsed_data[mapping[i["day_number"]]].append(i)
        
    for day, lessons in parsed_data.items():
        print(f"\nOn {day.upper()} you have:")
        for lesson in lessons:
            print(f"Lesson {lesson["cours_nr"]} | {lesson["teacher_name"]} |"
                  f"aud. {lesson["cours_office"] if lesson["cours_office"] else "Unknown"}") 