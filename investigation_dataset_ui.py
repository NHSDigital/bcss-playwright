import json
import streamlit as st
from datetime import datetime
from typing import Any, Optional
from enum import Enum
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
)

# --- Enum mapping ---
ENUM_MAP = {
    "YesNoOptions": YesNoOptions,
    "DrugTypeOptions": DrugTypeOptions,
    "BowelPreparationQualityOptions": BowelPreparationQualityOptions,
    "ComfortOptions": ComfortOptions,
    "EndoscopyLocationOptions": EndoscopyLocationOptions,
    "InsufflationOptions": InsufflationOptions,
    "OutcomeAtTimeOfProcedureOptions": OutcomeAtTimeOfProcedureOptions,
    "LateOutcomeOptions": LateOutcomeOptions,
    "CompletionProofOptions": CompletionProofOptions,
    "FailureReasonsOptions": FailureReasonsOptions,
    "PolypClassificationOptions": PolypClassificationOptions,
    "PolypAccessOptions": PolypAccessOptions,
    "PolypInterventionModalityOptions": PolypInterventionModalityOptions,
    "PolypInterventionDeviceOptions": PolypInterventionDeviceOptions,
    "PolypInterventionExcisionTechniqueOptions": PolypInterventionExcisionTechniqueOptions,
    "PolypTypeOptions": PolypTypeOptions,
    "AdenomaSubTypeOptions": AdenomaSubTypeOptions,
    "SerratedLesionSubTypeOptions": SerratedLesionSubTypeOptions,
    "PolypExcisionCompleteOptions": PolypExcisionCompleteOptions,
    "PolypDysplasiaOptions": PolypDysplasiaOptions,
    "YesNoUncertainOptions": YesNoUncertainOptions,
    "ReasonPathologyLostOptions": ReasonPathologyLostOptions,
    "PolypInterventionSuccessOptions": PolypInterventionSuccessOptions,
    "PolypReasonLeftInSituOptions": PolypReasonLeftInSituOptions,
    "AntibioticsAdministeredDrugTypeOptions": AntibioticsAdministeredDrugTypeOptions,
    "OtherDrugsAdministeredDrugTypeOptions": OtherDrugsAdministeredDrugTypeOptions,
}


# --- Utility pretty-print functions ---
def pretty_dict(d: dict, indent: int = 4) -> str:
    """
    Pretty-print a dictionary with indentation.
    Args:
        d (dict): The dictionary to pretty-print.
        indent (int): The number of spaces to use for indentation.
    Returns:
        str: The pretty-printed dictionary.
    """
    pad = " " * indent
    inner = []
    for k, v in d.items():
        key_str = f'"{k}"' if isinstance(k, str) else str(k)
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
    Pretty-print a list with indentation.
    Args:
        items (list): The list to pretty-print.
        indent (int): The number of spaces to use for indentation.
    Returns:
        str: The pretty-printed list.
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


# --- Load JSON field definitions ---
with open("investigation_dataset_ui_app/dataset_fields.json", "r") as f:
    FIELD_DEFS = json.load(f)

# --- Section names ---
SECTIONS = [
    "general_information",
    "drug_information",
    "endoscopy_information",
    "completion_information",
    "failure_information",
    "polyp_information_and_intervention_and_histology",
]

SECTION_LABELS = {
    "general_information": "General Information",
    "drug_information": "Drug Information",
    "endoscopy_information": "Endoscopy Information",
    "completion_information": "Completion Information",
    "failure_information": "Failure Information",
    "polyp_information_and_intervention_and_histology": "Polyp Information, Intervention & Histology",
}

# --- Main section selection ---
st.set_page_config(page_title="Investigation Dataset Builder", layout="wide")
st.sidebar.title("Sections")
section = st.sidebar.radio("Jump to", [SECTION_LABELS[s] for s in SECTIONS])


def render_field(field: dict, idx: Optional[int | str] = None) -> Any:
    """
    Render a single field based on its definition using match-case.
    Args:
        field (dict): The field definition.
        idx (int | str, optional): Index for repeated fields (e.g., polyp number).
    Returns:
        The value entered by the user, or None if not applicable.
    """
    key = field["key"]
    desc = field.get("description", "")
    optional = field.get("optional", False)
    field_type = field["type"]
    widget_key = f"{key}_{idx}" if idx is not None else key

    # Handle conditional fields (shown only if another field has a specific value)
    if "conditional_on" in field:
        cond = field["conditional_on"]
        cond_val = st.session_state.get(cond["field"])
        if cond_val != cond["value"]:
            return None

    # Optional field: show checkbox first
    if optional:
        show = st.checkbox(f"Add {key} ({desc})", key=f"chk_{widget_key}")
        if not show:
            return None

    match field_type:
        case "integer":
            return st.number_input(
                f"{key} ({desc})",
                min_value=field["range"][0],
                max_value=field["range"][1],
                key=widget_key,
            )
        case "integer_or_none":
            val_raw = st.text_input(f"{key} ({desc})", key=widget_key)
            return None if val_raw.strip() == "" else int(val_raw)
        case t if t in ENUM_MAP:
            return st.selectbox(
                f"{key} ({desc})",
                list(ENUM_MAP[field_type]),
                format_func=lambda x: x.name,
                key=widget_key,
            )
        case "string":
            return st.text_input(f"{key} ({desc})", key=widget_key)
        case "yes_no":
            return st.selectbox(f"{key} ({desc})", ["yes", "no"], key=widget_key)
        case "therapeutic_diagnostic":
            return st.selectbox(
                f"{key} ({desc})", ["therapeutic", "diagnostic"], key=widget_key
            )
        case "time":
            return st.text_input(
                f"{key} ({desc}) (HH:MM)", value="07:00", key=widget_key
            )
        case "datetime":
            return st.date_input(
                f"{key} ({desc})", value=datetime.today(), key=widget_key
            )
        case _:
            return st.text_input(f"{key} ({desc})", key=widget_key)


def show_section(section_name: str) -> None:
    """
    Show a section of the form based on its name.
    Args:
        section_name (str): The name of the section to show.
    """
    section = FIELD_DEFS[section_name]
    st.header(SECTION_LABELS[section_name])
    result = {}
    for field in section["fields"]:
        val = render_field(field)
        if val is not None:
            result[field["key"]] = val
    st.code(f"{section_name} = {pretty_dict(result)}", language="python")


def show_drug_information() -> None:
    """
    Show the Drug Information section, allowing multiple entries for each drug group.
    """
    st.header(SECTION_LABELS["drug_information"])
    drug_groups = FIELD_DEFS["drug_information"]["groups"]
    result = {}

    for group in drug_groups:
        st.subheader(group["label"])
        count = st.number_input(
            f"Number of {group['label'].lower()}",
            min_value=0,
            max_value=20,
            value=0,
            step=1,
            key=f"count_{group['label']}",
        )
        fields = group["fields"]
        for i in range(1, count + 1):
            col1, col2 = st.columns([2, 1])
            # Assume first field is type, second is dose
            type_field = fields[0]
            dose_field = fields[1]

            with col1:
                if type_field["type"] in ENUM_MAP:
                    dtype = st.selectbox(
                        f"{type_field['description']} {i}",
                        [""] + list(ENUM_MAP[type_field["type"]]),
                        format_func=lambda e: "—" if e == "" else e.name,
                        key=f"{type_field['key'].replace('X', str(i))}",
                    )
                else:
                    dtype = st.text_input(
                        f"{type_field['description']} {i}",
                        key=f"{type_field['key'].replace('X', str(i))}",
                    )
            with col2:
                ddose = st.text_input(
                    f"{dose_field['description']} {i}",
                    key=f"{dose_field['key'].replace('X', str(i))}",
                )
            # Only add if either field is filled
            if dtype != "" or ddose.strip() != "":
                result[type_field["key"].replace("X", str(i))] = dtype
                result[dose_field["key"].replace("X", str(i))] = ddose

    st.code(f"drug_information = {pretty_dict(result)}", language="python")


def show_polyp_information_and_intervention_and_histology() -> None:
    """
    Show the Polyp Information, Intervention & Histology section, allowing multiple polyps and interventions.
    Each polyp can have multiple interventions and optional histology.
    """
    st.header(SECTION_LABELS["polyp_information_and_intervention_and_histology"])
    polyp_info_fields = FIELD_DEFS["polyp_information"]["fields"]
    polyp_intervention_fields = FIELD_DEFS["polyp_intervention"]["fields"]
    polyp_histology_fields = FIELD_DEFS["polyp_histology"]["fields"]

    num_polyps = st.number_input(
        "Number of polyps", min_value=0, max_value=20, value=1, step=1
    )
    polyp_information, polyp_intervention, polyp_histology = [], [], []

    for pi in range(1, num_polyps + 1):
        st.markdown(f"### Polyp {pi}")
        polyp_entry = {}
        for field in polyp_info_fields:
            val = render_field(field, idx=pi)
            if val is not None:
                polyp_entry[field["key"]] = val
        polyp_information.append(polyp_entry)

        # Interventions: Only show if checkbox is checked
        interventions_for_polyp = []
        add_interventions = st.checkbox(
            f"Add interventions for polyp {pi}?", key=f"add_interventions_{pi}"
        )
        if add_interventions:
            num_int = st.number_input(
                f"Number of interventions for polyp {pi}",
                min_value=0,
                max_value=10,
                value=1,
                step=1,
                key=f"numint_{pi}",
            )
            for ij in range(1, num_int + 1):
                st.markdown(f"**Intervention {ij}**")
                int_dict = {}
                for field in polyp_intervention_fields:
                    val = render_field(field, idx=f"{pi}_{ij}")
                    if val is not None:
                        int_dict[field["key"]] = val
                interventions_for_polyp.append(int_dict)
        polyp_intervention.append(interventions_for_polyp)

        # Histology: Only show if checkbox is checked
        hist_dict = {}
        add_histology = st.checkbox(
            f"Add histology for polyp {pi}?", key=f"add_histology_{pi}"
        )
        if add_histology:
            for field in polyp_histology_fields:
                val = render_field(field, idx=pi)
                if val is not None:
                    hist_dict[field["key"]] = val
        polyp_histology.append(hist_dict)

    st.markdown("#### Output")
    st.code(f"polyp_information = {pretty_list(polyp_information)}", language="python")
    st.code(
        f"polyp_intervention = {pretty_list(polyp_intervention)}", language="python"
    )
    st.code(f"polyp_histology = {pretty_list(polyp_histology)}", language="python")


# --- Main page logic ---
if section == SECTION_LABELS["general_information"]:
    show_section("general_information")
elif section == SECTION_LABELS["drug_information"]:
    show_drug_information()
elif section == SECTION_LABELS["endoscopy_information"]:
    show_section("endoscopy_information")
elif section == SECTION_LABELS["completion_information"]:
    show_section("completion_information")
elif section == SECTION_LABELS["failure_information"]:
    show_section("failure_information")
elif section == SECTION_LABELS["polyp_information_and_intervention_and_histology"]:
    show_polyp_information_and_intervention_and_histology()
