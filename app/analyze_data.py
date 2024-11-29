""" 
Analyze data from db.

For each UC campus,
1. Total admission/application percentage across all schools and all races.
2. Total admission/application percentage across all schools for Asians.
3. Above stats for each year.

For each school,
1. Total admission/application percentage across all campuses and all races.
2. Total admission/application percentage across all campuses for Asians.
3. Above stats for each year.

* Missing data about school population.

"""

import logging
from collections import defaultdict
from sqlalchemy import func
from app.models import CountBySchool
from app.database import session_factory

logger = logging.getLogger(__name__)


def by_campus_rate() -> dict:
    with session_factory() as session:
        all_campuses_queryset = session.query(CountBySchool.campus).distinct().all()
        all_campuses = [_.campus for _ in all_campuses_queryset]
        print(f"Found distinct campuses: {all_campuses}")

        all_years_queryset = session.query(CountBySchool.year).distinct().all()
        all_years = [_.year for _ in all_years_queryset]
        print(f"Found distinct years: {all_years}")

        results = {}
        for campus in all_campuses:
            campus_res = {}
            for year in all_years:
                count_data = (
                    session.query(
                        CountBySchool.count_type, func.sum(CountBySchool.count)
                    )
                    .filter(
                        CountBySchool.year == year,
                        CountBySchool.campus == campus,
                        CountBySchool.race == "All",
                    )
                    .group_by(CountBySchool.count_type)
                    .all()
                )
                app_count = [_[1] for _ in count_data if _[0] == "App"][0]
                adm_count = [_[1] for _ in count_data if _[0] == "Adm"][0]

                asian_count_data = (
                    session.query(
                        CountBySchool.count_type, func.sum(CountBySchool.count)
                    )
                    .filter(
                        CountBySchool.year == year,
                        CountBySchool.campus == campus,
                        CountBySchool.race == "Asian",
                    )
                    .group_by(CountBySchool.count_type)
                    .all()
                )
                asian_app_count = [_[1] for _ in asian_count_data if _[0] == "App"][0]
                asian_adm_count = [_[1] for _ in asian_count_data if _[0] == "Adm"][0]

                campus_res[year] = {
                    "all_app": app_count,
                    "all_adm": adm_count,
                    "all_percentage": adm_count / app_count,
                    "asian_app": asian_app_count,
                    "asian_adm": asian_adm_count,
                    "asian_percentage": asian_adm_count / asian_app_count,
                }

            results[campus] = campus_res

        return results


def by_school_rate(select_campus: str = "individual") -> dict:
    """
    :param select_campus, str, can be "all", "individual", or specific campus name
    """
    with session_factory() as session:
        all_schools_queryset = session.query(CountBySchool.school).distinct().all()
        all_schools = [_.school for _ in all_schools_queryset]
        print(f"Found distinct schools: {all_schools}")

        all_years_queryset = session.query(CountBySchool.year).distinct().all()
        all_years = [_.year for _ in all_years_queryset]
        print(f"Found distinct years: {all_years}")

        all_campuses_queryset = session.query(CountBySchool.campus).distinct().all()
        all_campuses = [_.campus for _ in all_campuses_queryset]
        print(f"Found distinct campuses: {all_campuses}")

        results = {}
        skipped_school_count = 0
        all_school_count = 0
        for school in all_schools:
            all_school_count += 1
            school_res = {}
            for year in all_years:
                indiv_campus_dict = defaultdict(dict)

                select_clause = [CountBySchool.count_type]
                group_by_clause = [CountBySchool.count_type]
                filter_clause = [
                    CountBySchool.year == year,
                    CountBySchool.school == school,
                    CountBySchool.race == "All",
                ]
                if select_campus == "individual":
                    select_clause.append(CountBySchool.campus)
                    group_by_clause.append(CountBySchool.campus)
                elif select_campus != "all":
                    # specified a campus name
                    filter_clause.append(CountBySchool.campus == select_campus)

                select_clause.append(func.sum(CountBySchool.count))
                count_data = (
                    session.query(*select_clause)
                    .filter(*filter_clause)
                    .group_by(*group_by_clause)
                    .all()
                )

                if not count_data:
                    print(f"No count_data for {school=}, {year=}")
                    continue

                if select_campus == "individual":
                    for row in count_data:
                        if row[0] == "App":
                            indiv_campus_dict[row[1]]["all_app"] = row[2]
                        if row[0] == "Adm":
                            indiv_campus_dict[row[1]]["all_adm"] = row[2]
                    for k in indiv_campus_dict.keys():
                        indiv_campus_dict[k]["all_percentage"] = (
                            indiv_campus_dict[k].get("all_adm", 0)
                            / indiv_campus_dict[k].get("all_app", 0)
                            if indiv_campus_dict[k].get("all_app", 0) > 0
                            else None
                        )
                else:
                    app_count = [_[1] for _ in count_data if _[0] == "App"][0]
                    adm_count = [_[1] for _ in count_data if _[0] == "Adm"][0]

                filter_clause_2 = [
                    CountBySchool.year == year,
                    CountBySchool.school == school,
                    CountBySchool.race == "Asian",
                ]
                asian_count_data = (
                    session.query(*select_clause)
                    .filter(*filter_clause_2)
                    .group_by(*group_by_clause)
                    .all()
                )
                if select_campus == "individual":
                    for row in asian_count_data:
                        if row[0] == "App":
                            indiv_campus_dict[row[1]]["asian_app"] = row[2]
                        if row[0] == "Adm":
                            indiv_campus_dict[row[1]]["asian_adm"] = row[2]
                    for k in indiv_campus_dict.keys():
                        indiv_campus_dict[k]["asian_percentage"] = (
                            indiv_campus_dict[k].get("asian_adm", 0)
                            / indiv_campus_dict[k].get("asian_app", 0)
                            if indiv_campus_dict[k].get("asian_app", 0) > 0
                            else None
                        )
                else:
                    asian_app_count = [_[1] for _ in asian_count_data if _[0] == "App"][
                        0
                    ]
                    asian_adm_count = [_[1] for _ in asian_count_data if _[0] == "Adm"][
                        0
                    ]
                if select_campus == "individual":
                    no_data = True
                    for k, v in indiv_campus_dict.items():
                        if v["asian_percentage"] or v["all_percentage"]:
                            no_data = False
                            break
                    if no_data:
                        print(
                            f"Skip school for year because admission rate is 0 or no data: {school}/{year}"
                        )
                        continue
                    school_res[year] = dict(indiv_campus_dict)
                else:
                    if not adm_count and not asian_adm_count:
                        print(
                            f"Skip school for year because admission rate is 0 or no data: {school}/{year}"
                        )
                        continue
                    school_res[year] = {
                        "all_app": app_count,
                        "all_adm": adm_count,
                        "all_percentage": adm_count / app_count if app_count else None,
                        "asian_app": asian_app_count,
                        "asian_adm": asian_adm_count,
                        "asian_percentage": (
                            asian_adm_count / asian_app_count
                            if asian_app_count
                            else None
                        ),
                    }

            if school_res:
                results[school] = school_res
            else:
                skipped_school_count += 1
                print(f"Skip school because admission rate is 0 or no data: {school}")

        print(
            f"Total {all_school_count} schools found and skipped {skipped_school_count}."
        )

        # sort by highest all_percentage in 2023
        if select_campus != "individual":
            results = dict(
                sorted(
                    results.items(),
                    key=lambda x: (
                        x[1]["2023"]["all_percentage"]
                        if x[1].get("2023", {}).get("all_percentage")
                        else 0
                    ),
                    reverse=True,
                )
            )

        return results
