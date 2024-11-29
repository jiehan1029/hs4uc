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
from app.models import CountBySchool, HighSchool, HSPopulation
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


def by_school_rate(
    select_campus: str = "individual", select_year: str | int = "all"
) -> dict:
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

        loop_years = all_years
        if select_year != "all":
            if str(select_year) in all_years:
                loop_years = [str(select_year)]

        sort_by_year = str(max([int(_) for _ in loop_years]))

        print(f"Loop data for years: {loop_years}")

        all_campuses_queryset = session.query(CountBySchool.campus).distinct().all()
        all_campuses = [_.campus for _ in all_campuses_queryset]
        print(f"Found distinct campuses: {all_campuses}")

        results = {}
        skipped_school_count = 0
        all_school_count = 0
        for school in all_schools:
            all_school_count += 1
            school_res = {}
            for year in loop_years:

                ######### Get student demographics data ##################
                # get the high school 12th grade enrollment population
                hs_enr_data = (
                    session.query(HSPopulation.race, HSPopulation.count)
                    .join(HighSchool, HighSchool.id == HSPopulation.school_id)
                    .filter(
                        HighSchool.name == school,
                        HSPopulation.count_type == "hs_enr",
                        HSPopulation.year == year,
                    )
                    .all()
                )
                all_enr_count = None
                asian_enr_count = None
                if hs_enr_data:
                    all_enr_count = [_.count for _ in hs_enr_data if _.race == "All"]
                    all_enr_count = all_enr_count[0] if all_enr_count else None
                    asian_enr_count = [
                        _.count for _ in hs_enr_data if _.race == "Asian"
                    ]
                    asian_enr_count = asian_enr_count[0] if asian_enr_count else None

                student_demo = {
                    "all_student_count": all_enr_count,
                    "asian_student_count": asian_enr_count,
                    "asian_student_percentage": (
                        asian_enr_count / all_enr_count
                        if (asian_enr_count and all_enr_count)
                        else 0
                    ),
                }

                ########## Get admission/application rate ####################
                indiv_campus_dict = defaultdict(lambda: defaultdict(dict))
                select_clause = [CountBySchool.count_type]
                group_by_clause = [CountBySchool.count_type]
                filter_clause = [
                    CountBySchool.year == year,
                    CountBySchool.school == school,
                    CountBySchool.race == "All",
                ]
                filter_clause_2 = [
                    CountBySchool.year == year,
                    CountBySchool.school == school,
                    CountBySchool.race == "Asian",
                ]
                if select_campus == "individual":
                    select_clause.append(CountBySchool.campus)
                    group_by_clause.append(CountBySchool.campus)
                elif select_campus != "all":
                    # specified a campus name
                    filter_clause.append(CountBySchool.campus == select_campus)
                    filter_clause_2.append(CountBySchool.campus == select_campus)

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
                            indiv_campus_dict[row[1]]["admission/application"][
                                "all_app"
                            ] = row[2]
                        if row[0] == "Adm":
                            indiv_campus_dict[row[1]]["admission/application"][
                                "all_adm"
                            ] = row[2]
                    for k in indiv_campus_dict.keys():
                        indiv_campus_dict[k]["admission/application"][
                            "all_percentage"
                        ] = (
                            indiv_campus_dict[k]["admission/application"].get(
                                "all_adm", 0
                            )
                            / indiv_campus_dict[k]["admission/application"].get(
                                "all_app", 0
                            )
                            if indiv_campus_dict[k]["admission/application"].get(
                                "all_app", 0
                            )
                            > 0
                            else None
                        )
                else:
                    app_count = [_[1] for _ in count_data if _[0] == "App"][0]
                    adm_count = [_[1] for _ in count_data if _[0] == "Adm"][0]
                    enr_count = [_[1] for _ in count_data if _[0] == "Enr"]
                    enr_count = enr_count[0] if enr_count else None

                asian_count_data = (
                    session.query(*select_clause)
                    .filter(*filter_clause_2)
                    .group_by(*group_by_clause)
                    .all()
                )
                if select_campus == "individual":
                    for row in asian_count_data:
                        if row[0] == "App":
                            indiv_campus_dict[row[1]]["admission/application"][
                                "asian_app"
                            ] = row[2]
                        if row[0] == "Adm":
                            indiv_campus_dict[row[1]]["admission/application"][
                                "asian_adm"
                            ] = row[2]
                    for k in indiv_campus_dict.keys():
                        indiv_campus_dict[k]["admission/application"][
                            "asian_percentage"
                        ] = (
                            indiv_campus_dict[k]["admission/application"].get(
                                "asian_adm", 0
                            )
                            / indiv_campus_dict[k]["admission/application"].get(
                                "asian_app", 0
                            )
                            if indiv_campus_dict[k]["admission/application"].get(
                                "asian_app", 0
                            )
                            > 0
                            else None
                        )
                else:
                    asian_app_count = [_[1] for _ in asian_count_data if _[0] == "App"][
                        0
                    ]
                    asian_adm_count = [_[1] for _ in asian_count_data if _[0] == "Adm"][
                        0
                    ]
                    asian_enr_count = [_[1] for _ in asian_count_data if _[0] == "Enr"]
                    asian_enr_count = asian_enr_count[0] if asian_enr_count else None

                ########## Get application/total student percentage ####################
                app_student_data = {}
                if select_campus == "individual":
                    for k, v in indiv_campus_dict.items():
                        v["application/student"]["all_app_all_student"] = (
                            v["admission/application"].get("all_app", 0) / all_enr_count
                            if all_enr_count
                            else None
                        )
                        v["application/student"]["asian_app_asian_student"] = (
                            v["admission/application"].get("asian_app", 0)
                            / asian_enr_count
                            if asian_enr_count
                            else None
                        )
                        v["application/student"]["asian_app_all_student"] = (
                            v["admission/application"].get("asian_app", 0)
                            / all_enr_count
                            if all_enr_count
                            else None
                        )
                        v["application/student"]["all_adm_all_student"] = (
                            v["admission/application"].get("all_adm", 0) / all_enr_count
                            if all_enr_count
                            else None
                        )
                        v["application/student"]["asian_adm_asian_student"] = (
                            v["admission/application"].get("asian_adm", 0)
                            / asian_enr_count
                            if asian_enr_count
                            else None
                        )
                        v["application/student"]["asian_adm_all_student"] = (
                            v["admission/application"].get("asian_adm", 0)
                            / all_enr_count
                            if all_enr_count
                            else None
                        )
                else:
                    app_student_data["all_app_all_student"] = (
                        app_count / all_enr_count if all_enr_count else None
                    )
                    app_student_data["asian_app_asian_student"] = (
                        asian_app_count / asian_enr_count
                        if (asian_app_count and asian_enr_count)
                        else 0
                    )
                    app_student_data["asian_app_all_student"] = (
                        asian_app_count / all_enr_count
                        if (asian_app_count and all_enr_count)
                        else 0
                    )
                    app_student_data["all_adm_all_student"] = (
                        adm_count / all_enr_count if all_enr_count else None
                    )
                    app_student_data["asian_adm_asian_student"] = (
                        asian_adm_count / asian_enr_count
                        if (asian_adm_count and asian_enr_count)
                        else 0
                    )
                    app_student_data["asian_adm_all_student"] = (
                        asian_adm_count / all_enr_count
                        if (asian_adm_count and all_enr_count)
                        else 0
                    )

                ########## Get campus enrollment/admission percentage ####################
                # the lower the enrollment/admission percentage, the larger chance that the student
                # land on a better university.
                enr_adm_data = {}
                if select_campus == "individual":
                    v["enrollment/admission"]["all_enr_count"] = enr_count
                    v["enrollment/admission"]["asian_enr_count"] = asian_enr_count
                    v["enrollment/admission"]["all_enr_all_adm"] = (
                        enr_count / v["admission/application"].get("all_adm")
                        if v["admission/application"].get("all_adm") and enr_count
                        else None
                    )
                    v["enrollment/admission"]["asian_enr_asian_adm"] = (
                        asian_enr_count / v["admission/application"].get("asian_adm")
                        if v["admission/application"].get("asian_adm")
                        and asian_enr_count
                        else None
                    )
                    v["enrollment/admission"]["asian_enr_all_adm"] = (
                        asian_enr_count / v["admission/application"].get("all_adm")
                        if v["admission/application"].get("all_adm") and asian_enr_count
                        else None
                    )
                else:
                    enr_adm_data["all_enr_count"] = enr_count
                    enr_adm_data["asian_enr_count"] = asian_enr_count
                    enr_adm_data["all_enr_all_adm"] = (
                        enr_count / adm_count if (adm_count and enr_count) else None
                    )
                    enr_adm_data["asian_enr_asian_adm"] = (
                        asian_enr_count / asian_adm_count
                        if (asian_adm_count and asian_enr_count)
                        else None
                    )
                    enr_adm_data["asian_enr_all_adm"] = (
                        asian_enr_count / adm_count
                        if (adm_count and asian_enr_count)
                        else None
                    )

                if select_campus == "individual":
                    no_data = True
                    for k, v in indiv_campus_dict.items():
                        if (
                            v["admission/application"]["asian_percentage"]
                            or v["admission/application"]["all_percentage"]
                        ):
                            no_data = False
                            break
                    if no_data:
                        print(
                            f"Skip school for year because admission rate is 0 or no data: {school}/{year}"
                        )
                        continue
                    school_res[year] = {
                        "student_demo": student_demo,
                        **dict(indiv_campus_dict),
                    }
                else:
                    if not adm_count and not asian_adm_count:
                        print(
                            f"Skip school for year because admission rate is 0 or no data: {school}/{year}"
                        )
                        continue
                    school_res[year] = {
                        "student_demo": student_demo,
                        "application/student": app_student_data,
                        "admission/application": {
                            "all_app": app_count,
                            "all_adm": adm_count,
                            "all_percentage": (
                                adm_count / app_count if app_count else None
                            ),
                            "asian_app": asian_app_count,
                            "asian_adm": asian_adm_count,
                            "asian_percentage": (
                                asian_adm_count / asian_app_count
                                if asian_app_count
                                else None
                            ),
                        },
                        "enrollment/admission": enr_adm_data,
                    }

            if school_res:
                # sort by most recent year
                sorted_school_res = dict(sorted(school_res.items(), reverse=True))
                results[school] = sorted_school_res
            else:
                skipped_school_count += 1
                print(f"Skip school because admission rate is 0 or no data: {school}")

        print(
            f"Total {all_school_count} schools found and skipped {skipped_school_count}."
        )

        # sort by highest all_adm_all_student
        # secondary sort by lowest all_enr_all_adm
        if select_campus != "individual":
            results = dict(
                sorted(
                    results.items(),
                    key=lambda x: (
                        (
                            x[1][sort_by_year]["application/student"][
                                "all_adm_all_student"
                            ]
                            if x[1]
                            .get(sort_by_year, {})
                            .get("application/student", {})
                            .get("all_adm_all_student")
                            else 0
                        ),
                        (
                            -1
                            * x[1][sort_by_year]["enrollment/admission"][
                                "all_enr_all_adm"
                            ]
                            if x[1]
                            .get(sort_by_year, {})
                            .get("enrollment/admission", {})
                            .get("all_enr_all_adm")
                            else -10
                        ),
                    ),
                    reverse=True,
                )
            )

        return results
