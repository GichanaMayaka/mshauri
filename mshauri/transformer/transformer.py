from collections import defaultdict
from enum import Enum

import numpy as np
import pandas as pd

from ..extensions import db
from ..models import CME, Drill, MentorsChecklist


class EssentialTopics(Enum):
    ESSENTIAL_DRILLS = {
        "Eclampsia",
    }
    ESSENTIAL_CMES = {
        "Postpartum haemorrhage (PPH)",
        "Infection prevention",
    }


def process(
    source: pd.DataFrame,
) -> tuple[tuple[defaultdict, defaultdict], tuple[defaultdict, defaultdict]]:
    """Processes the source dataframe and returns Participant and Topic[s] information as tuples

    Args:
        source (pd.DataFrame): The source data as a Pandas Dataframe

    Returns:
        tuple[tuple[defaultdict, defaultdict], tuple[defaultdict, defaultdict]]: The CME Topics,
        CME Participants as a the first tuple, and Drill Topics, and Drill Participants as the
        second tuple respectively
    """
    # Columns mask
    cme_cols_mask = source.columns.str.contains("cme/id_number")
    drill_cols_mask = source.columns.str.contains("drill/id_drill")
    cme_topics_cols_mask = source.columns.str.contains("cme_topic")
    drill_topics_cols_mask = source.columns.str.contains("drill_topic")

    facilities_cols_mask = source.columns.str.contains("facility")
    facility_columns = source.columns[facilities_cols_mask].to_list()

    # CME details returned
    cme_participants_details = defaultdict(set)
    cme_topics_details = defaultdict(list)

    # Drill details returned
    drill_participants_details = defaultdict(set)
    drill_topics_details = defaultdict(list)

    for index, row in source.iterrows():
        facility = (
            row[facility_columns].dropna().values[0]
        )  # Assumption is each observation will occur on/have only one facility associated
        facility_info = facility.split("_", 1)
        facility_code = facility_info[0]
        facility_name = facility_info[1]

        cme_participants = row[cme_cols_mask].dropna()
        cme_participants_details[row["_id"]].update(cme_participants)

        drill_participants = row[drill_cols_mask].dropna()
        drill_participants_details[row["_id"]].update(drill_participants)

        cmes = row[cme_topics_cols_mask].dropna()
        for cme in cmes:
            cme_detail = (
                row[
                    "mentor_checklist/cme_grp/cme_completion_date"
                ],  # Static Information
                cme,
                row["mentor_checklist/mentor/q_county"],  # Static Information
                row["_submission_time"],
                None,
                None,
                None,
                facility_code,
                facility_name,
                row["mentor_checklist/mentor/name"],  # Static Information
            )  # None for columns where the information isn't needed at this stage
            cme_topics_details[row._id].append(cme_detail)

            if row["mentor_checklist/cme_grp/cme_total"] == 2:
                cme_topics_details[row._id].append(cme_detail)

        drills = row[drill_topics_cols_mask].dropna()
        for drill in drills:
            drill_det = (
                row[
                    "mentor_checklist/cme_grp/cme_completion_date"
                ],  # Static Information
                None,
                row["mentor_checklist/mentor/q_county"],  # Static Information
                row["_submission_time"],
                drill,
                None,
                None,
                facility_code,
                facility_name,
                row["mentor_checklist/mentor/name"],  # Static Information
                None,
            )  # None for columns where the information isn't needed at this stage
            drill_topics_details[row._id].append(drill_det)

            if row["mentor_checklist/drills_grp/drills_total"] == 2:
                drill_topics_details[row._id].append(drill_det)

    return (cme_topics_details, cme_participants_details), (
        drill_topics_details,
        drill_participants_details,
    )


def generate_target_dataframe(
    cme_participants: defaultdict,
    cme_topics: defaultdict,
    drill_participants: defaultdict,
    drill_topics,
) -> pd.DataFrame:
    """Generates a Dataframe from the Participants and Topics information.

    Args:
        cme_participants (defaultdict): The CME Participants in each observation
        cme_topics (defaultdict): The CME topics in each observation
        drill_participants (defaultdict): The Drill Participants in each observation
        drill_topics (_type_): The Drill topics in each observation

    Returns:
        pd.DataFrame: The resultant Dataframe
    """
    columns = [
        "id",
        "cme_completion_date",
        "cme_topic",
        "county",
        "date_submitted",
        "drill_topic",
        "essential_cme_topic",
        "essential_drill_topic",
        "facility_code",
        "facility_name",
        "mentor_name",
        "id_number_cme",
        "id_number_drill",
        "submission_id",
        "success_story",
    ]

    # Perform "cartesian product" of participants and topics for each observation
    cme_details = [
        (None, *detail, participant, None, submission_id, None)
        for submission_id, details in cme_topics.items()
        for detail in details
        for participant in cme_participants[submission_id]
    ]

    drill_details = [
        (None, *detail, participant, submission_id, None)
        for submission_id, details in drill_topics.items()
        for detail in details
        for participant in drill_participants[submission_id]
    ]

    cme_details.extend(drill_details)

    return pd.DataFrame(cme_details, columns=columns)


def parser(source: pd.DataFrame) -> pd.DataFrame:
    """Build the final resulting dataframe

    Args:
        source (pd.DataFrame): Source dataframe

    Returns:
        pd.DataFrame: Output processed dataframe
    """
    (cme_topics, cme_participants), (drill_topics, drill_participants) = process(source)
    output = generate_target_dataframe(
        cme_participants, cme_topics, drill_participants, drill_topics
    )

    unique_cmes = output.cme_topic.dropna().unique().tolist()
    unique_drills = output.drill_topic.dropna().unique().tolist()

    for cme in unique_cmes:
        # Save set of CMEs to db if they don't exist
        new_cme = CME.get_by_name(cme) or CME.create(name=cme)
        output["cme_unique_id"] = np.where(
            output["cme_topic"] == cme, new_cme, output.get("cme_unique_id", np.nan)
        )

    for drill in unique_drills:
        # Save set of Drills to db if they don't exist
        new_drill = Drill.get_by_name(drill) or Drill.create(name=drill)
        output["drill_unique_id"] = np.where(
            output["drill_topic"] == drill,
            new_drill,
            output.get("drill_unique_id", np.nan),
        )

    output["essential_drill_topic"] = output.apply(
        lambda r: (r["drill_topic"] in EssentialTopics.ESSENTIAL_DRILLS.value),
        axis=1,
    )
    output["essential_cme_topic"] = output.apply(
        lambda r: (r["cme_topic"] in EssentialTopics.ESSENTIAL_CMES.value),
        axis=1,
    )
    output.drop(["cme_topic", "drill_topic", "id"], axis=1, inplace=True)

    output.to_sql(
        MentorsChecklist.__tablename__,
        con=db.engine,
        if_exists="append",
        index=False,
    )

    return output
