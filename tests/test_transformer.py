from collections import defaultdict

import pandas as pd

from mshauri.transformer import generate_target_dataframe, process


def test_process(test_dataframe):
    """Test transformer.process() function"""
    out = process(test_dataframe)
    (cme_topic, cme_participants), (drill_topics, drill_participants) = out

    assert isinstance(out, tuple)
    assert len(out) == 2
    assert len(out[0]) == 2
    assert len(out[1]) == 2

    assert isinstance(cme_topic, defaultdict)
    assert isinstance(cme_participants, defaultdict)
    assert isinstance(drill_topics, defaultdict)
    assert isinstance(drill_participants, defaultdict)

    # Exptected outputs
    assert cme_participants == {464111771: {712345678}}
    assert cme_topic == {
        464111771: [
            (
                "2023-08-03",
                "Hypertension_in_pregnancy",
                "Bungoma",
                "2023-08-10T15:01:24",
                None,
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
            ),
            (
                "2023-08-03",
                "Hypertension_in_pregnancy",
                "Bungoma",
                "2023-08-10T15:01:24",
                None,
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
            ),
            (
                "2023-08-03",
                "Postpartum_haemorrhage_(PPH)",
                "Bungoma",
                "2023-08-10T15:01:24",
                None,
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
            ),
            (
                "2023-08-03",
                "Postpartum_haemorrhage_(PPH)",
                "Bungoma",
                "2023-08-10T15:01:24",
                None,
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
            ),
        ]
    }

    assert drill_participants == {464111771: {789765432}}
    assert drill_topics == {
        464111771: [
            (
                "2023-08-03",
                None,
                "Bungoma",
                "2023-08-10T15:01:24",
                "Eclampsia",
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
                None,
            ),
            (
                "2023-08-03",
                None,
                "Bungoma",
                "2023-08-10T15:01:24",
                "Eclampsia",
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
                None,
            ),
            (
                "2023-08-03",
                None,
                "Bungoma",
                "2023-08-10T15:01:24",
                "Shoulder_dystocia_birth_of_a_non-vigorou",
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
                None,
            ),
            (
                "2023-08-03",
                None,
                "Bungoma",
                "2023-08-10T15:01:24",
                "Shoulder_dystocia_birth_of_a_non-vigorou",
                None,
                None,
                "15808",
                "Bokoli_Hospital",
                "Dr Lex",
                None,
            ),
        ]
    }


def test_generate_target_dataframe(test_dataframe):
    """Tests transformer.generate_target_dataframe() function"""
    out = process(test_dataframe)
    (cme_topic, cme_participants), (drill_topics, drill_participants) = out

    df = generate_target_dataframe(
        cme_topics=cme_topic,
        cme_participants=cme_participants,
        drill_participants=drill_participants,
        drill_topics=drill_topics,
    )

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (8, 15)

    assert len(df.cme_topic.dropna().unique().tolist()) == 2
    assert len(df.drill_topic.dropna().unique().tolist()) == 2

    assert len(df.facility_name.dropna().unique().tolist()) == 1
    assert df.facility_name.dropna().unique().tolist()[0] == "Bokoli_Hospital"
    assert df.facility_code.dropna().unique().tolist()[0] == "15808"

    assert df.id_number_cme.count() == df.id_number_drill.count()
