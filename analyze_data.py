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
from sqlalchemy import func
from models import CountBySchool
from database import session_factory

logger = logging.getLogger(__name__)


def by_campus_rate() -> dict:
    with session_factory() as session:
        all_campuses_queryset = session.query(CountBySchool.campus).distinct().all()
        all_campuses = [_.campus for _ in all_campuses_queryset]
        logger.info(f"Found distinct campuses: {all_campuses}")

        all_years_queryset = session.query(CountBySchool.year).distinct().all()
        all_years = [_.year for _ in all_years_queryset]
        logger.info(f"Found distinct years: {all_years}")

        results = {}
        for campus in all_campuses:
            campus_res = {}
            for year in all_years:
                app_count = (
                    session.query(func.sum(CountBySchool.count))
                    .filter(
                        CountBySchool.count_type == "App",
                        CountBySchool.year == year,
                        CountBySchool.campus == campus,
                        CountBySchool.race == "All",
                    )
                    .scalar()
                )
                # app_count=app_count.count
                adm_count = (
                    session.query(func.sum(CountBySchool.count))
                    .filter(
                        CountBySchool.count_type == "Adm",
                        CountBySchool.year == year,
                        CountBySchool.campus == campus,
                        CountBySchool.race == "All",
                    )
                    .scalar()
                )
                # adm_count=adm_count.count

                asian_app_count = (
                    session.query(func.sum(CountBySchool.count))
                    .filter(
                        CountBySchool.count_type == "App",
                        CountBySchool.year == year,
                        CountBySchool.campus == campus,
                        CountBySchool.race == "Asian",
                    )
                    .scalar()
                )
                # asian_app_count=asian_app_count.count
                asian_adm_count = (
                    session.query(func.sum(CountBySchool.count))
                    .filter(
                        CountBySchool.count_type == "Adm",
                        CountBySchool.year == year,
                        CountBySchool.campus == campus,
                        CountBySchool.race == "Asian",
                    )
                    .scalar()
                )
                # asian_adm_count=asian_adm_count.count

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
