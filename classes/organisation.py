class Organisation:
    def __init__(self, organisation_id: str):
        self.organisation_id = organisation_id

    def get_organisation_id(self) -> str:
        return self.organisation_id
