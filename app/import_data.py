"""
parse csv and save to db
"""

import logging
import pandas as pd
from sqlalchemy import func
from app.models import CountBySchool, HighSchool, HSPopulation
from app.database import session_factory

logger = logging.getLogger(__name__)


DEFAULT_FILE_PATH = "~/Desktop/admissions.xlsx"
YEARS = ["2023", "2022", "2021"]
CAMPUSES = ["ucb", "ucla", "uci", "ucd"]

DEFAULT_FILE_PATH_GRAD_STATS = "~/Desktop/hs_graduates.xlsx"
GRAD_YEARS = ["2023", "2021"]

SHEET_HEADER_TO_TABLE_COLUMNS = {
    "Calculation1": "na",
    "County/State/ Territory": "na",
    "School": "school",
    "City": "city",
    "Count": "count_type",
}


def read_file_to_list(
    file_path: str, sheet_name: str | int | None = 0, ffill: bool = True
) -> list[dict]:
    raw_df = pd.read_excel(io=file_path, sheet_name=sheet_name, header=0)
    if ffill:
        columns_to_ffill = ["Calculation1", "County/State/ Territory", "School", "City"]
        raw_df[columns_to_ffill] = raw_df[columns_to_ffill].ffill()
    raw_df.fillna(0, inplace=True)
    # pd.set_option("display.max_columns", None)
    # print(f"****** raw_df\n{raw_df}")
    records = raw_df.to_dict("records")
    return records


def save_file_to_db(file_path: str = DEFAULT_FILE_PATH) -> dict:
    results = {}
    with session_factory() as session:
        for yr in YEARS:
            for camp in CAMPUSES:
                sheet_name = f"{yr} {camp}"
                records = read_file_to_list(file_path=file_path, sheet_name=sheet_name)
                new_saved = 0
                existing_count = 0
                for rec in records:
                    # match schools
                    school_id = None
                    found_school = (
                        session.query(HighSchool.id)
                        .filter(
                            HighSchool.city == rec.get("City"),
                            HighSchool.name == rec.get("School"),
                        )
                        .first()
                    )
                    if found_school:
                        school_id = found_school.id
                    else:
                        new_school = HighSchool(
                            city=rec.get("City"),
                            name=rec.get("School"),
                        )
                        session.add(new_school)
                        session.commit()
                        session.refresh(new_school)
                        school_id = new_school.id
                        print(f"Created new school {new_school.name}({new_school.id})")

                    races = [
                        _
                        for _ in rec.keys()
                        if SHEET_HEADER_TO_TABLE_COLUMNS.get(_) is None
                    ]
                    for race in races:
                        try:
                            existing = (
                                session.query(CountBySchool.id)
                                .filter(
                                    CountBySchool.year == yr,
                                    CountBySchool.campus == camp,
                                    CountBySchool.race == race,
                                    CountBySchool.count_type == rec.get("Count"),
                                    CountBySchool.count == rec.get(race, 0),
                                    CountBySchool.city == rec.get("City"),
                                    CountBySchool.school == rec.get("School"),
                                )
                                .first()
                            )
                            if existing is None:
                                new_obj = CountBySchool(
                                    year=yr,
                                    campus=camp,
                                    race=race,
                                    count_type=rec.get("Count"),
                                    count=rec.get(race, 0),
                                    city=rec.get("City"),
                                    school=rec.get("School"),
                                    school_id=school_id,
                                )
                                session.add(new_obj)
                                new_saved += 1
                            else:
                                if existing.school_id is None:
                                    existing.school_id = school_id
                                existing_count += 1
                            session.commit()
                        except Exception as e:
                            logger.error(e)
                            session.rollback()

                results[sheet_name] = {
                    "new_saved": new_saved,
                    "existing": existing_count,
                }

    return results


def save_grad_population_to_db(file_path: str = DEFAULT_FILE_PATH_GRAD_STATS) -> dict:
    race_shortname_map = {"ALL": "All", "AS": "Asian"}
    # todo/note: two spreadsheets may use different names for the same school.
    school_name_map = {
        "adrian wilcox high": "ADRIAN C WILCOX HIGH SCHOOL",
        "andrew p. hill high": "ANDREW P HILL HIGH SCHOOL",
        "downtown college preparatory": "DOWNTOWN COLG PREP EL PRIMERO",  # uncertain accuracy
        "downtown college prep - alum rock": "DOWNTOWN COLLEGE PREP ALUM ROC",
        "dr. tj owens gilroy early college academy": "DR TJ OWENS GILROY EARLY COLG",
        "henry m. gunn high": "HENRY M GUNN SENIOR HIGH SCHL",
        "gunderson high": "HENRY T GUNDERSON HIGH SCHOOL",
        "latino college preparatory academy": "LATINO COLLEGE PREP ACADEMY",
        "liberty (alternative)": "LIBERTY HIGH SCHOOL",
        "milpitas middle college high": "MILPITAS MIDDLE COLLEGE HS",
        "mission early college high": "MISSION EARLY COLLEGE HIGH SCH",
        "mt. pleasant high": "MOUNT PLEASANT HIGH SCHOOL",
        "palo alto high": "PALO ALTO SENIOR HIGH SCHOOL",
        "b. roberto cruz leadership academy": "ROBERTO CRUZ LEADERSHIP ACDMY",
        "summit public school: denali": "SUMMIT PUBLIC SCHOOL DENALI",
        "summit public school: tahoma": "SUMMIT PUBLIC SCHOOL-TAHOMA",
        "university preparatory academy charter": "UNIVERSITY PREP ACADEMY",
        "william c. overfelt high": "W C OVERFELT HIGH SCHOOL",
        "wilson alternative": "WILSON HIGH SCHOOL",
    }
    results = {"new_saved": 0, "updated": 0, "existing_unchanged": 0, "error": 0}
    with session_factory() as session:
        for year in GRAD_YEARS:
            records = read_file_to_list(
                file_path=file_path, sheet_name=year, ffill=False
            )
            for rec in records:
                # only check school data
                if rec["rtype"].lower() != "s":
                    continue

                # only check SC county
                if rec["countyname"].lower() != "santa clara":
                    continue

                # only check all and asian stats
                if rec["studentgroup"] not in ["ALL", "AS"]:
                    continue
                try:
                    school_name = rec["schoolname"].strip().lower()
                    school_name_2 = school_name + " " + "school"
                    school_name_3 = school_name_map.get(school_name)
                    school_names = [school_name, school_name_2]
                    if school_name_3:
                        school_names.append(school_name_3.lower())
                    found_school = (
                        session.query(HighSchool.id)
                        .filter(func.lower(HighSchool.name).in_(school_names))
                        .first()
                    )
                    if not found_school:
                        print(f"Cannot find school {school_name}, skip importing.")
                        continue

                    race = race_shortname_map[rec["studentgroup"]]
                    count = rec["currdenom"]
                    # check if already imported the population object
                    found_population = (
                        session.query(HSPopulation.id, HSPopulation.count)
                        .filter(
                            HSPopulation.school_id == found_school.id,
                            HSPopulation.race == race,
                            HSPopulation.year == year,
                            HSPopulation.count_type == "hs_enr",
                        )
                        .first()
                    )
                    if found_population:
                        if found_population.count != count:
                            found_population.count = count
                            results["updated"] += 1
                        else:
                            results["existing_unchanged"] += 1
                    else:
                        # add new obj
                        new_poulation = HSPopulation(
                            school_id=found_school.id,
                            race=race,
                            year=year,
                            count_type="hs_enr",
                            count=count,
                        )
                        session.add(new_poulation)
                        results["new_saved"] += 1
                    session.commit()

                    # also save prior year's data
                    last_year = str(int(year) - 1)
                    last_year_count = rec.get("priordenom")
                    if last_year_count is not None:
                        found_last_population = (
                            session.query(HSPopulation.id, HSPopulation.count)
                            .filter(
                                HSPopulation.school_id == found_school.id,
                                HSPopulation.race == race,
                                HSPopulation.year == last_year,
                                HSPopulation.count_type == "hs_enr",
                            )
                            .first()
                        )
                        if found_last_population:
                            if found_last_population.count != last_year_count:
                                found_last_population.count = last_year_count
                                results["updated"] += 1
                            else:
                                results["existing_unchanged"] += 1
                        else:
                            # add new obj
                            new_last_poulation = HSPopulation(
                                school_id=found_school.id,
                                race=race,
                                year=last_year,
                                count_type="hs_enr",
                                count=last_year_count,
                            )
                            session.add(new_last_poulation)
                            results["new_saved"] += 1
                        session.commit()
                except Exception as e:
                    print(e)
                    session.rollback()
                    results["error"] += 1

    return results
