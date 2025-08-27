from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class PISubject:
    """
    Represents a PI Subject with all relevant demographic and administrative fields.
    """

    screening_subject_id: Optional[int] = None
    nhs_number: Optional[str] = None
    family_name: Optional[str] = None
    first_given_names: Optional[str] = None
    other_given_names: Optional[str] = None
    previous_family_name: Optional[str] = None
    name_prefix: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    gender_code: Optional[int] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    address_line_4: Optional[str] = None
    address_line_5: Optional[str] = None
    postcode: Optional[str] = None
    gnc_code: Optional[str] = None
    gp_practice_code: Optional[str] = None
    nhais_deduction_reason: Optional[str] = None
    nhais_deduction_date: Optional[date] = None
    exeter_system: Optional[str] = None
    removed_to: Optional[str] = None
    pi_reference: Optional[str] = None
    superseded_by_nhs_number: Optional[str] = None
    replaced_nhs_number: Optional[str] = None

    def get_screening_subject_id(self) -> Optional[int]:
        """Returns the screening subject ID."""
        return self.screening_subject_id

    def set_screening_subject_id(self, screening_subject_id: int) -> None:
        """Sets the screening subject ID."""
        self.screening_subject_id = screening_subject_id

    def get_nhs_number(self) -> Optional[str]:
        """Returns the NHS number."""
        return self.nhs_number

    def set_nhs_number(self, nhs_number: str) -> None:
        """Sets the NHS number."""
        self.nhs_number = nhs_number

    def get_family_name(self) -> Optional[str]:
        """Returns the family name."""
        return self.family_name

    def set_family_name(self, family_name: str) -> None:
        """Sets the family name."""
        self.family_name = family_name

    def get_first_given_names(self) -> Optional[str]:
        """Returns the first given names."""
        return self.first_given_names

    def set_first_given_names(self, first_given_names: str) -> None:
        """Sets the first given names."""
        self.first_given_names = first_given_names

    def get_other_given_names(self) -> Optional[str]:
        """Returns the other given names."""
        return self.other_given_names

    def set_other_given_names(self, other_given_names: str) -> None:
        """Sets the other given names."""
        self.other_given_names = other_given_names

    def get_previous_family_name(self) -> Optional[str]:
        """Returns the previous family name."""
        return self.previous_family_name

    def set_previous_family_name(self, previous_family_name: str) -> None:
        """Sets the previous family name."""
        self.previous_family_name = previous_family_name

    def get_name_prefix(self) -> Optional[str]:
        """Returns the name prefix."""
        return self.name_prefix

    def set_name_prefix(self, name_prefix: str) -> None:
        """Sets the name prefix."""
        self.name_prefix = name_prefix

    def get_birth_date(self) -> Optional[date]:
        """Returns the birth date."""
        return self.birth_date

    def set_birth_date(self, birth_date: date) -> None:
        """Sets the birth date."""
        self.birth_date = birth_date

    def get_death_date(self) -> Optional[date]:
        """Returns the death date."""
        return self.death_date

    def set_death_date(self, death_date: Optional[date]) -> None:
        """Sets the death date."""
        self.death_date = death_date

    def get_gender_code(self) -> Optional[int]:
        """Returns the gender code."""
        return self.gender_code

    def set_gender_code(self, gender_code: int) -> None:
        """Sets the gender code."""
        self.gender_code = gender_code

    def get_address_line1(self) -> Optional[str]:
        """Returns address line 1."""
        return self.address_line_1

    def set_address_line1(self, address_line1: str) -> None:
        """Sets address line 1."""
        self.address_line_1 = address_line1

    def get_address_line2(self) -> Optional[str]:
        """Returns address line 2."""
        return self.address_line_2

    def set_address_line2(self, address_line2: str) -> None:
        """Sets address line 2."""
        self.address_line_2 = address_line2

    def get_address_line3(self) -> Optional[str]:
        """Returns address line 3."""
        return self.address_line_3

    def set_address_line3(self, address_line3: str) -> None:
        """Sets address line 3."""
        self.address_line_3 = address_line3

    def get_address_line4(self) -> Optional[str]:
        """Returns address line 4."""
        return self.address_line_4

    def set_address_line4(self, address_line4: str) -> None:
        """Sets address line 4."""
        self.address_line_4 = address_line4

    def get_address_line5(self) -> Optional[str]:
        """Returns address line 5."""
        return self.address_line_5

    def set_address_line5(self, address_line5: str) -> None:
        """Sets address line 5."""
        self.address_line_5 = address_line5

    def get_post_code(self) -> Optional[str]:
        """Returns the post code."""
        return self.postcode

    def set_post_code(self, post_code: str) -> None:
        """Sets the post code."""
        self.postcode = post_code

    def get_exeter_system(self) -> Optional[str]:
        """Returns the Exeter system."""
        return self.exeter_system

    def set_exeter_system(self, exeter_system: str) -> None:
        """Sets the Exeter system."""
        self.exeter_system = exeter_system

    def get_removed_to(self) -> Optional[str]:
        """Returns the removed to field."""
        return self.removed_to

    def set_removed_to(self, removed_to: Optional[str]) -> None:
        """Sets the removed to field."""
        self.removed_to = removed_to

    def get_superseded_by_nhs_number(self) -> Optional[str]:
        """Returns the superseded by NHS number."""
        return self.superseded_by_nhs_number

    def set_superseded_by_nhs_number(
        self, superseded_by_nhs_number: Optional[str]
    ) -> None:
        """Sets the superseded by NHS number."""
        self.superseded_by_nhs_number = superseded_by_nhs_number

    def get_replaced_by_nhs_number(self) -> Optional[str]:
        """Returns the replaced by NHS number."""
        return self.replaced_nhs_number

    def set_replaced_by_nhs_number(self, replaced_by_nhs_number: Optional[str]) -> None:
        """Sets the replaced by NHS number."""
        self.replaced_nhs_number = replaced_by_nhs_number

    def get_registration_code(self) -> Optional[str]:
        """Returns the registration code."""
        return self.gnc_code

    def set_registration_code(self, registration_code: str) -> None:
        """Sets the registration code."""
        self.gnc_code = registration_code

    def get_gp_practice_code(self) -> Optional[str]:
        """Returns the GP practice code."""
        return self.gp_practice_code

    def set_gp_practice_code(self, gp_practice_code: str) -> None:
        """Sets the GP practice code."""
        self.gp_practice_code = gp_practice_code

    def get_nhais_deduction_reason(self) -> Optional[str]:
        """Returns the NHAIS deduction reason."""
        return self.nhais_deduction_reason

    def set_nhais_deduction_reason(self, nhais_deduction_reason: Optional[str]) -> None:
        """Sets the NHAIS deduction reason."""
        self.nhais_deduction_reason = nhais_deduction_reason

    def get_nhais_deduction_date(self) -> Optional[date]:
        """Returns the NHAIS deduction date."""
        return self.nhais_deduction_date

    def set_nhais_deduction_date(self, nhais_deduction_date: Optional[date]) -> None:
        """Sets the NHAIS deduction date."""
        self.nhais_deduction_date = nhais_deduction_date

    def get_pi_reference(self) -> Optional[str]:
        """Returns the PI reference."""
        return self.pi_reference

    def set_pi_reference(self, pi_reference: str) -> None:
        """Sets the PI reference."""
        self.pi_reference = pi_reference

    def to_string(self) -> str:
        """
        Returns a string representation of the PISubject object, showing all field names and values.
        Each field is on a new line with extra spacing for readability.
        Useful for logging and debugging.
        """
        fields = [
            f"screening_subject_id    =    {self.screening_subject_id}",
            f"nhs_number              =    {self.nhs_number}",
            f"family_name             =    {self.family_name}",
            f"first_given_names       =    {self.first_given_names}",
            f"other_given_names       =    {self.other_given_names}",
            f"previous_family_name    =    {self.previous_family_name}",
            f"name_prefix             =    {self.name_prefix}",
            f"birth_date              =    {self.birth_date}",
            f"death_date              =    {self.death_date}",
            f"gender_code             =    {self.gender_code}",
            f"address_line1           =    {self.address_line_1}",
            f"address_line2           =    {self.address_line_2}",
            f"address_line3           =    {self.address_line_3}",
            f"address_line4           =    {self.address_line_4}",
            f"address_line5           =    {self.address_line_5}",
            f"post_code               =    {self.postcode}",
            f"registration_code       =    {self.gnc_code}",
            f"gp_practice_code        =    {self.gp_practice_code}",
            f"nhais_deduction_reason  =    {self.nhais_deduction_reason}",
            f"nhais_deduction_date    =    {self.nhais_deduction_date}",
            f"exeter_system           =    {self.exeter_system}",
            f"removed_to              =    {self.removed_to}",
            f"pi_reference            =    {self.pi_reference}",
            f"superseded_by_nhs_number=    {self.superseded_by_nhs_number}",
            f"replaced_by_nhs_number  =    {self.replaced_nhs_number}",
        ]
        return "PISubject:\n" + "\n".join(fields)
