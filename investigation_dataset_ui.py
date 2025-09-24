import streamlit as st
from datetime import datetime, date, time
from enum import Enum
from typing import Any, Callable
from pages.datasets.investigation_dataset_page import (
    DrugTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    EndoscopyLocationOptions,
    YesNoOptions,
    InsufflationOptions,
    OutcomeAtTimeOfProcedureOptions,
    LateOutcomeOptions,
    CompletionProofOptions,
    FailureReasonsOptions,
    PolypClassificationOptions,
    PolypAccessOptions,
    PolypInterventionModalityOptions,
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
    PolypTypeOptions,
    AdenomaSubTypeOptions,
    SerratedLesionSubTypeOptions,
    PolypExcisionCompleteOptions,
    PolypDysplasiaOptions,
    YesNoUncertainOptions,
    ReasonPathologyLostOptions,
    PolypInterventionSuccessOptions,
    PolypReasonLeftInSituOptions,
    AntibioticsAdministeredDrugTypeOptions,
    OtherDrugsAdministeredDrugTypeOptions,
    EndoscopeNotInsertedOptions,
    SedationOptions,
)

# TODO: Add EndoscopeNotInsertedOptions and SedationOptions here and to the utility

st.set_page_config(page_title="Investigation Dataset Builder", layout="wide")

# -------------------------
# Constants:
# -------------------------
general_info_str = "General Information"
drug_info_str = "Drug Information"
endoscopy_info_str = "Endoscopy Information"
instructions_str = "Instructions"


# -------------------------
# Helper: Manage times
# -------------------------
START_LIMIT = time(7, 0)
END_LIMIT = time(19, 0)


def time_field(label: str, key: str) -> time:
    """
    Show a time input field with a warning if outside 07:00-19:00.
    Args:
        label (str): The label for the time input field.
        key (str): The key for the time input field.
    Returns:
        time: The selected time.
    """
    # let user pick or type any time (24h) but start at 07:00 by default
    t = st.time_input(label, value=START_LIMIT, key=key)

    # warn if outside the allowed window
    if t < START_LIMIT or t > END_LIMIT:
        st.warning(
            f"⚠️ {label} should be between {START_LIMIT.strftime('%H:%M')} "
            f"and {END_LIMIT.strftime('%H:%M')}"
        )
    return t


# -------------------------
# Formatting code outputs
# -------------------------
def pretty_dict(d: dict, indent: int = 4) -> str:
    """
    Format a dict into a multi-line, Python-style string with
    pretty printing for dicts and Enums.
    Args:
        d (dict): The dictionary to format.
        indent (int): The number of spaces to indent each line.
    Returns:
        str: The formatted string.
    """
    pad = " " * indent
    inner = []
    for k, v in d.items():
        # Format key with double quotes
        key_str = f'"{k}"' if isinstance(k, str) else str(k)
        # Format value
        if isinstance(v, Enum):
            val = f"{v.__class__.__name__}.{v.name}"
        elif isinstance(v, dict):
            val = pretty_dict(v, indent + 4).replace("\n", "\n" + pad)
        elif isinstance(v, list):
            val = pretty_list(v, indent + 4).replace("\n", "\n" + pad)
        elif isinstance(v, str):
            val = f'"{v}"'
        else:
            val = str(v)
        inner.append(f"{key_str}: {val}")
    joined = (",\n" + pad).join(inner)
    return "{" + ("\n" + pad + joined + "\n" if inner else "") + "}"


def pretty_list(items: list, indent: int = 4) -> str:
    """
    Format a list into a multi-line, Python-style string with
    pretty printing for dicts and Enums.
    Args:
        items (list): The list to format.
        indent (int): The number of spaces to indent each line.
    Returns:
        str: The formatted string.
    """
    pad = " " * indent
    inner = []
    for x in items:
        if isinstance(x, dict):
            inner.append(pretty_dict(x, indent).replace("\n", "\n" + pad))
        elif isinstance(x, list):
            inner.append(pretty_list(x, indent).replace("\n", "\n" + pad))
        elif isinstance(x, Enum):
            inner.append(f"{x.__class__.__name__}.{x.name}")
        elif isinstance(x, str):
            inner.append(f'"{x}"')
        else:
            inner.append(str(x))
    joined = (",\n" + pad).join(inner)
    return "[" + ("\n" + pad + joined + "\n" if inner else "") + "]"


# -------------------------
# Making Inputs Optional
# -------------------------
def optional_input(label: str, widget_fn: Callable, *args, **kwargs):
    """
    Show a checkbox to include/exclude an optional input widget.
    Args:
        label (str): The label for the checkbox and widget.
        widget_fn (callable): The Streamlit widget function to call if included.
        *args: Positional arguments to pass to the widget function.
        **kwargs: Keyword arguments to pass to the widget function.
    Returns:
        tuple: (include (bool), value): Whether the input was included, and its value if so.
    """
    cols = st.columns([0.25, 0.75])
    with cols[0]:
        include = st.checkbox(f"Add {label}", key=f"chk_{kwargs.get('key','')}")
    val = None
    with cols[1]:
        if include:
            # just take the widget return unchanged
            val = widget_fn(label, *args, **kwargs)
    return include, val


# -------------------------
# PREVIEW & EXPORT
# -------------------------
def py_repr(obj: Any) -> str:
    """
    Return a Python-style string representation of an object, with special handling for
    Enums, datetimes, dates, lists, and dicts.
    Args:
        obj (Any): The object to represent.
    Returns:
        str: The Python-style string representation.
    """
    # Enums
    if isinstance(obj, Enum):
        return f"{obj.__class__.__name__}.{obj.name}"
    if isinstance(obj, datetime):
        return f"datetime({obj.year}, {obj.month}, {obj.day})"
    if isinstance(obj, date):
        return f"datetime({obj.year}, {obj.month}, {obj.day})"
    if obj is None:
        return "None"
    if isinstance(obj, str):
        return repr(obj)
    if isinstance(obj, list):
        inner = ", ".join(py_repr(x) for x in obj)
        return f"[{inner}]"
    if isinstance(obj, dict):
        inner = ", ".join(f"{repr(k)}: {py_repr(v)}" for k, v in obj.items())
        return "{" + inner + "}"
    return repr(obj)


# -------------------------
# NEW: Instructions
# -------------------------


def show_instructions():
    """
    Show instructions for using the utility.
    """
    st.title("Investigation Dataset Builder Utility")
    st.markdown(
        """
        ### How to use this utility

        1. **Navigate** between sections using the sidebar.
        2. **Fill in** the required and optional fields in each section.
        3. **Copy** the generated Python dictionary code snippets for use in your tests or scripts.

        ---
        """
    )


def show_general_information():
    """
    Show the General Information section.
    """
    st.header(general_info_str)

    site_idx = st.number_input(
        "Site lookup index (int) — use -1 to pick last or not found",
        value=-1,
        step=1,
        format="%d",
    )
    practitioner_idx = st.number_input(
        "Practitioner index (int) — use -1 to pick last or not found",
        value=-1,
        step=1,
        format="%d",
    )
    testing_clinician_idx = st.number_input(
        "Testing Clinician index (int) — use -1 to pick last or not found",
        value=-1,
        step=1,
        format="%d",
    )
    aspirant_idx_raw = st.text_input(
        "Aspirant Endoscopist index (int or blank for None)", value=""
    )
    aspirant_idx = None if aspirant_idx_raw.strip() == "" else int(aspirant_idx_raw)

    general_information = {
        "site": int(site_idx),
        "practitioner": int(practitioner_idx),
        "testing clinician": int(testing_clinician_idx),
        "aspirant endoscopist": aspirant_idx,
    }

    st.code(
        "general_information = " + pretty_dict(general_information),
        language="python",
    )


def show_drug_information():
    """
    Show the Drug Information section.
    """
    st.header(drug_info_str)

    st.subheader("Bowel preparation (drug_typeX / drug_doseX)")
    bowel_count = st.number_input(
        "Number of bowel preparation entries",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
    )
    bowel_entries = []
    for i in range(1, bowel_count + 1):
        col1, col2 = st.columns([2, 1])
        with col1:
            dtype = st.selectbox(
                f"Drug type {i}",
                [""] + list(DrugTypeOptions),
                format_func=lambda e: "—" if e == "" else e.name,
                key=f"drugtype_bowel_{i}",
            )
        with col2:
            ddose = st.text_input(f"Drug dose {i}", value="", key=f"drugdose_bowel_{i}")
        bowel_entries.append((dtype, ddose))

    st.subheader("Antibiotics (antibiotic_drug_typeX / antibiotic_drug_doseX)")
    ab_count = st.number_input(
        "Number of antibiotic entries", min_value=0, max_value=100, value=0, step=1
    )
    ab_entries = []
    for i in range(1, ab_count + 1):
        col1, col2 = st.columns([2, 1])
        with col1:
            atype = st.selectbox(
                f"Antibiotic type {i}",
                [""] + list(AntibioticsAdministeredDrugTypeOptions),
                format_func=lambda e: "—" if e == "" else e.name,
                key=f"abtype_{i}",
            )
        with col2:
            adose = st.text_input(f"Antibiotic dose {i}", value="", key=f"abdose_{i}")
        ab_entries.append((atype, adose))

    st.subheader("Other drugs (other_drug_typeX / other_drug_doseX)")
    other_count = st.number_input(
        "Number of other drug entries", min_value=0, max_value=100, value=0, step=1
    )
    other_entries = []
    for i in range(1, other_count + 1):
        col1, col2 = st.columns([2, 1])
        with col1:
            otype = st.selectbox(
                f"Other drug type {i}",
                [""] + list(OtherDrugsAdministeredDrugTypeOptions),
                format_func=lambda e: "—" if e == "" else e.name,
                key=f"otype_{i}",
            )
        with col2:
            odose = st.text_input(f"Other drug dose {i}", value="", key=f"odose_{i}")
        other_entries.append((otype, odose))

    drug_information = {}
    for idx, (t, d) in enumerate(bowel_entries, start=1):
        drug_information[f"drug_type{idx}"] = t
        drug_information[f"drug_dose{idx}"] = d

    for idx, (t, d) in enumerate(ab_entries, start=1):
        drug_information[f"antibiotic_drug_type{idx}"] = t
        drug_information[f"antibiotic_drug_dose{idx}"] = d

    for idx, (t, d) in enumerate(other_entries, start=1):
        drug_information[f"other_drug_type{idx}"] = t
        drug_information[f"other_drug_dose{idx}"] = d

    st.code(
        "drug_information = " + pretty_dict(drug_information),
        language="python",
    )


def show_endoscopy_information():
    """
    Show the Endoscopy Information section.
    """
    st.header(endoscopy_info_str)

    endoscope_inserted = st.selectbox("Endoscope inserted", ["yes", "no"])
    procedure_type = st.selectbox("Procedure type", ["therapeutic", "diagnostic"])
    bowel_quality = st.selectbox(
        "Bowel preparation quality",
        list(BowelPreparationQualityOptions),
        format_func=lambda e: e.name,
    )
    comfort_exam = st.selectbox(
        "Comfort during examination", list(ComfortOptions), format_func=lambda e: e.name
    )
    comfort_recovery = st.selectbox(
        "Comfort during recovery", list(ComfortOptions), format_func=lambda e: e.name
    )
    endoscopist_extent = st.selectbox(
        "Endoscopist defined extent",
        list(EndoscopyLocationOptions),
        format_func=lambda e: e.name,
    )
    scope_imager_used = st.selectbox(
        "Scope imager used", list(YesNoOptions), format_func=lambda e: e.name
    )
    retroverted_view = st.selectbox(
        "Retroverted view", list(YesNoOptions), format_func=lambda e: e.name
    )
    start_of_intubation_time = time_field("Start of intubation time", "intub")
    start_of_extubation_time = time_field("Start of extubation time", "extub")
    end_time_of_procedure = time_field("End time of procedure", "endproc")
    scope_id = st.text_input("Scope ID", value="Autotest")
    insufflation = st.selectbox(
        "Insufflation", list(InsufflationOptions), format_func=lambda e: e.name
    )
    outcome_at_time = st.selectbox(
        "Outcome at time of procedure",
        list(OutcomeAtTimeOfProcedureOptions),
        format_func=lambda e: e.name,
    )
    late_outcome = st.selectbox(
        "Late outcome", list(LateOutcomeOptions), format_func=lambda e: e.name
    )

    endoscopy_information = {
        "endoscope inserted": endoscope_inserted,
        "procedure type": procedure_type,
        "bowel preparation quality": bowel_quality,
        "comfort during examination": comfort_exam,
        "comfort during recovery": comfort_recovery,
        "endoscopist defined extent": endoscopist_extent,
        "scope imager used": scope_imager_used,
        "retroverted view": retroverted_view,
        "start of intubation time": start_of_intubation_time.strftime("%H:%M"),
        "start of extubation time": start_of_extubation_time.strftime("%H:%M"),
        "end time of procedure": end_time_of_procedure.strftime("%H:%M"),
        "scope id": scope_id,
        "insufflation": insufflation,
        "outcome at time of procedure": outcome_at_time,
        "late outcome": late_outcome,
    }

    st.code(
        "endoscopy_information = " + pretty_dict(endoscopy_information),
        language="python",
    )


def show_failure_completion_information():
    """
    Show the Failure & Completion Proof Information section.
    """
    st.header("Failure & Completion Proof Information")

    # Failure reasons
    st.subheader("Failure reasons")
    failure_reasons_selected = st.selectbox(
        "Failure reasons",
        options=list(FailureReasonsOptions),
        format_func=lambda e: e.name,
    )
    failure_information = {
        "failure reasons": failure_reasons_selected
        or [FailureReasonsOptions.NO_FAILURE_REASONS]
    }

    st.code(
        "failure_information = " + pretty_dict(failure_information),
        language="python",
    )

    # Completion proof (optional)
    st.subheader("Completion proof (optional)")
    completion_proof_val = st.selectbox(
        "Select completion proof options",
        options=list(CompletionProofOptions),
        format_func=lambda e: e.name,
    )
    completion_information = None
    if completion_proof_val:
        completion_information = {"completion proof": completion_proof_val}

        st.code(
            "completion_information = " + pretty_dict(completion_information),
            language="python",
        )


def polyp_info_fields(pi: int) -> list:
    """
    Show fields for a single polyp entry.
    Args:
        pi (int): The polyp index (1-based).
    Returns:
        list: A list of tuples (label, widget_fn, args, kwargs) for the
    """
    fields = [
        (
            "Location",
            st.selectbox,
            [list(EndoscopyLocationOptions)],
            {"format_func": lambda e: e.name, "key": f"loc_{pi}"},
        ),
        (
            "Classification",
            st.selectbox,
            [list(PolypClassificationOptions)],
            {"format_func": lambda e: e.name, "key": f"class_{pi}"},
        ),
        ("Estimate of whole polyp size (mm)", st.text_input, [], {"key": f"size_{pi}"}),
        (
            "Polyp access",
            st.selectbox,
            [list(PolypAccessOptions)],
            {"format_func": lambda e: e.name, "key": f"access_{pi}"},
        ),
        (
            "Secondary piece",
            st.selectbox,
            [list(YesNoOptions)],
            {"format_func": lambda x: x.name, "key": f"secondary_{pi}"},
        ),
        (
            "Left in situ",
            st.selectbox,
            [list(YesNoOptions)],
            {"format_func": lambda x: x.name, "key": f"left_{pi}"},
        ),
        (
            "Reason left in situ",
            st.selectbox,
            [list(PolypReasonLeftInSituOptions)],
            {"format_func": lambda x: x.name, "key": f"leftreason_{pi}"},
        ),
    ]
    return fields


def polyp_intervention_fields(pi: int, ij: int) -> list:
    """
    Show fields for a single polyp intervention entry.
    Args:
        pi (int): The polyp index (1-based).
        ij (int): The intervention index (1-based).
    Returns:
        list: A list of tuples (label, widget_fn, args, kwargs) for the
    """
    fields = [
        (
            "Modality",
            st.selectbox,
            [list(PolypInterventionModalityOptions)],
            {"format_func": lambda x: x.name, "key": f"mod_{pi}_{ij}"},
        ),
        (
            "Device",
            st.selectbox,
            [list(PolypInterventionDeviceOptions)],
            {"format_func": lambda x: x.name, "key": f"dev_{pi}_{ij}"},
        ),
        (
            "Excised",
            st.selectbox,
            [list(YesNoOptions)],
            {"format_func": lambda x: x.name, "key": f"exc_{pi}_{ij}"},
        ),
        (
            "Retrieved",
            st.selectbox,
            [list(YesNoOptions)],
            {"format_func": lambda x: x.name, "key": f"ret_{pi}_{ij}"},
        ),
        (
            "Excision technique",
            st.selectbox,
            [list(PolypInterventionExcisionTechniqueOptions)],
            {"format_func": lambda x: x.name, "key": f"exctech_{pi}_{ij}"},
        ),
        (
            "Polyp appears fully resected endoscopically",
            st.selectbox,
            [list(YesNoOptions)],
            {"format_func": lambda x: x.name, "key": f"appear_{pi}_{ij}"},
        ),
        (
            "Intervention success",
            st.selectbox,
            [list(PolypInterventionSuccessOptions)],
            {"format_func": lambda x: x.name, "key": f"intsucc_{pi}_{ij}"},
        ),
    ]
    return fields


def polyp_histology_fields(pi: int) -> list:
    """
    Show fields for a single polyp histology entry.
    Args:
        pi (int): The polyp index (1-based).
    Returns:
        list: A list of tuples (label, widget_fn, args, kwargs) for the
    """
    fields = [
        (
            "Pathology lost",
            st.selectbox,
            [list(YesNoOptions)],
            {"format_func": lambda x: x.name, "key": f"pathlost_{pi}"},
        ),
        (
            "Reason pathology lost",
            st.selectbox,
            [list(ReasonPathologyLostOptions)],
            {"format_func": lambda x: x.name, "key": f"reaspath_{pi}"},
        ),
        (
            "Date of reporting",
            st.date_input,
            [],
            {"value": date.today(), "key": f"date_rep_{pi}"},
        ),
        (
            "Date of receipt",
            st.date_input,
            [],
            {"value": date.today(), "key": f"date_recv_{pi}"},
        ),
        (
            "Pathology provider index",
            st.number_input,
            [],
            {"value": -1, "step": 1, "key": f"prov_{pi}"},
        ),
        (
            "Pathologist index",
            st.number_input,
            [],
            {"value": -1, "step": 1, "key": f"path_{pi}"},
        ),
        ("Polyp size (histology)", st.text_input, [], {"key": f"polpsz_{pi}"}),
    ]
    return fields


def handle_polyp_type(key_prefix: str, hist_dict: dict) -> None:
    """
    Handle polyp type and sub-type logic.
    Args:
        key_prefix (str): Unique key prefix, e.g. "2_1" for polyp 2, intervention 1.
        hist_dict (dict): The histology dictionary to update.
    """
    inc, val = optional_input(
        f"Polyp type (polyp {key_prefix.replace('_', ' int ')})",
        st.selectbox,
        list(PolypTypeOptions),
        format_func=lambda x: x.name,
        key=f"ptype_{key_prefix}",
    )
    if inc:
        hist_dict["polyp type"] = val
        if val == PolypTypeOptions.ADENOMA:
            inc, sub = optional_input(
                f"Adenoma sub type (polyp {key_prefix.replace('_', ' int ')})",
                st.selectbox,
                list(AdenomaSubTypeOptions),
                format_func=lambda x: x.name,
                key=f"adsub_{key_prefix}",
            )
            if inc:
                hist_dict["adenoma sub type"] = sub
        elif val == PolypTypeOptions.SERRATED_LESION:
            inc, sub = optional_input(
                f"Serrated lesion sub type (polyp {key_prefix.replace('_', ' int ')})",
                st.selectbox,
                list(SerratedLesionSubTypeOptions),
                format_func=lambda x: x.name,
                key=f"serrsub_{key_prefix}",
            )
            if inc:
                hist_dict["serrated lesion sub type"] = sub


def handle_polyp_histology_options(key_prefix: str, hist_dict: dict) -> None:
    """
    Handle additional polyp histology options.
    Args:
        key_prefix (str): Unique key prefix, e.g. "2_1" for polyp 2, intervention 1.
        hist_dict (dict): The histology dictionary to update.
    """
    for label, widget, options, kw in [
        (
            "Polyp excision complete",
            st.selectbox,
            list(PolypExcisionCompleteOptions),
            {"format_func": lambda x: x.name, "key": f"excomplete_{key_prefix}"},
        ),
        (
            "Polyp dysplasia",
            st.selectbox,
            list(PolypDysplasiaOptions),
            {"format_func": lambda x: x.name, "key": f"pdys_{key_prefix}"},
        ),
        (
            "Polyp carcinoma",
            st.selectbox,
            list(YesNoUncertainOptions),
            {"format_func": lambda x: x.name, "key": f"pcarc_{key_prefix}"},
        ),
    ]:
        inc, val = optional_input(
            f"{label} (polyp {key_prefix.replace('_', ' int ')})", widget, options, **kw
        )
        if inc:
            hist_dict[label.lower()] = val


def render_polyp_info(pi: int) -> dict:
    """
    Render polyp information fields for a single polyp.
    Args:
        pi (int): The polyp index (1-based).
    Returns:
        dict: The polyp information dictionary.
    """
    polyp_entry = {}
    for label, widget, args, kw in polyp_info_fields(pi):
        inc, val = optional_input(f"{label} (polyp {pi})", widget, *args, **kw)
        if inc:
            polyp_entry[label.lower()] = val
    return polyp_entry


def render_interventions(pi: int) -> list:
    """
    Render intervention fields for a single polyp, each with optional histology.
    Args:
        pi (int): The polyp index (1-based).
    Returns:
        list: A list of intervention dictionaries for the polyp.
    """
    interventions_for_polyp = []
    if st.checkbox(f"Add intervention(s) for polyp {pi}?", key=f"addint_{pi}"):
        num_int = st.number_input(
            f"Number of interventions for polyp {pi}",
            min_value=1,
            max_value=100,
            value=1,
            step=1,
            key=f"numint_{pi}",
        )
        for ij in range(1, num_int + 1):
            st.markdown(f"**Intervention {ij}**")
            int_dict = {}
            for label, widget, args, kw in polyp_intervention_fields(pi, ij):
                inc, val = optional_input(
                    f"{label} (polyp {pi} int {ij})", widget, *args, **kw
                )
                if inc:
                    int_dict[label.lower()] = val
            interventions_for_polyp.append(int_dict)
    return interventions_for_polyp


def render_histology(pi: int) -> dict:
    """
    Render histology fields for a single polyp.
    Args:
        pi (int): The polyp index (1-based).
    Returns:
        dict: The histology dictionary for this polyp.
    """
    hist_dict = {}
    if st.checkbox(f"Add histology for polyp {pi}?", key=f"addhist_{pi}"):
        for label, widget, args, kw in polyp_histology_fields(pi):
            inc, val = optional_input(f"{label} (polyp {pi})", widget, *args, **kw)
            if inc:
                hist_dict[label.lower()] = val
        handle_polyp_type(str(pi), hist_dict)
        handle_polyp_histology_options(str(pi), hist_dict)
    return hist_dict


def show_polyp_information():
    """
    Show the Polyp Information section.
    """
    st.header("Polyp Information (all keys optional)")

    num_polyps = st.number_input(
        "Number of polyps", min_value=0, max_value=100, value=1, step=1
    )

    polyp_information, polyp_intervention, polyp_histology = [], [], []

    for pi in range(1, num_polyps + 1):
        st.markdown(f"## Polyp {pi}")

        st.subheader(f"Polyp {pi} Information")
        polyp_information.append(render_polyp_info(pi))

        st.subheader(f"Polyp {pi} Intervention(s)")
        polyp_intervention.append(render_interventions(pi))

        st.subheader(f"Polyp {pi} Histology")
        polyp_histology.append(render_histology(pi))

    # OUTPUT
    st.markdown("### Generated polyp dictionaries (aligned lists)")
    st.write("polyp_information:")
    st.code(
        "polyp_information = " + pretty_list(polyp_information),
        language="python",
    )
    st.write("polyp_intervention:")
    st.code(
        "polyp_intervention = " + pretty_list(polyp_intervention),
        language="python",
    )
    st.write("polyp_histology:")
    st.code(
        "polyp_histology = " + pretty_list(polyp_histology),
        language="python",
    )


# -------------------------
# UI: Sidebar sections
# -------------------------
st.sidebar.title("Sections")
section = st.sidebar.radio(
    "Jump to",
    [
        instructions_str,
        general_info_str,
        drug_info_str,
        endoscopy_info_str,
        "Failure / Completion Information",
        "Polyp Information",
    ],
)


if section == instructions_str:
    show_instructions()
if section == general_info_str:
    show_general_information()
elif section == drug_info_str:
    show_drug_information()
elif section == endoscopy_info_str:
    show_endoscopy_information()
elif section == "Failure / Completion Information":
    show_failure_completion_information()
elif section == "Polyp Information":
    show_polyp_information()
