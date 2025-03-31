from playwright.sync_api import Page


class ScreeningStatusSearchOptions:
    CALL_STATUS = "4001"
    INACTIVE_STATUS = "4002"
    RECALL_STATUS = "4004"
    OPT_IN_STATUS = "4003"
    SELF_REFERRAL_STATUS = "4005"
    SURVEILLANCE_STATUS = "4006"
    SEEKING_FURTHER_DATA_STATUS = "4007"
    CEASED_STATUS = "4008"
    BOWEL_SCOPE_STATUS = "4009"
    LYNCH_SURVEILLANCE_STATUS = "306442"
    LYNCH_SELF_REFERRAL_STATUS = "307129"

    def __init__(self, page: Page):
        self.page = page

        # Locate screening status dropdown list
        self.select_status = self.page.locator("#A_C_ScreeningStatus")

    # Select screening status options
    def select_status_call(self)->None:
        self.select_status.select_option(self.CALL_STATUS)

    def select_status_inactive(self)->None:
        self.select_status.select_option(self.INACTIVE_STATUS)

    def select_status_recall(self)->None:
        self.select_status.select_option(self.RECALL_STATUS)

    def select_status_opt_in(self)->None:
        self.select_status.select_option(self.OPT_IN_STATUS)

    def select_status_self_referral(self)->None:
        self.select_status.select_option(self.SELF_REFERRAL_STATUS)

    def select_status_surveillance(self)->None:
        self.select_status.select_option(self.SURVEILLANCE_STATUS)

    def select_status_seeking_further_data(self)->None:
        self.select_status.select_option(self.SEEKING_FURTHER_DATA_STATUS)

    def select_status_ceased(self)->None:
        self.select_status.select_option(self.CEASED_STATUS)

    def select_status_bowel_scope(self)->None:
        self.select_status.select_option(self.BOWEL_SCOPE_STATUS)

    def select_status_lynch_surveillance(self)->None:
        self.select_status.select_option(self.LYNCH_SURVEILLANCE_STATUS)

    def select_status_lynch_self_referral(self)->None:
        self.select_status.select_option(self.LYNCH_SELF_REFERRAL_STATUS)


class LatestEpisodeStatusSearchOptions:
    OPEN_PAUSED_STATUS = "1"
    CLOSED_STATUS = "2"
    NO_EPISODE_STATUS = "3"

    def __init__(self, page: Page):
        self.page = page

        # Locate latest episode status status dropdown list
        self.select_status = self.page.locator("#A_C_EpisodeStatus")

    # Select latest episode status options
    def select_status_open_paused(self)->None:
        self.select_status.select_option(self.OPEN_PAUSED_STATUS)

    def select_status_closed(self)->None:
        self.select_status.select_option(self.CLOSED_STATUS)

    def select_status_no_episode(self)->None:
        self.select_status.select_option(self.NO_EPISODE_STATUS)


class SearchAreaSearchOptions:
    SEARCH_AREA_HOME_HUB = "01"
    SEARCH_AREA_GP_PRACTICE = "02"
    SEARCH_AREA_CCG = "03"
    SEARCH_AREA_SCREENING_CENTRE = "05"
    SEARCH_AREA_OTHER_HUB = "06"
    SEARCH_AREA_WHOLE_DATABASE = "07"

    def __init__(self, page: Page):
        self.page = page

        # Locate search area dropdown list
        self.select_area = self.page.locator("#A_C_SEARCH_DOMAIN")

    # Select search area options
    def select_search_area_home_hub(self)->None:
        self.select_area.select_option(self.SEARCH_AREA_HOME_HUB)

    def select_search_area_gp_practice(self)->None:
        self.select_area.select_option(self.SEARCH_AREA_GP_PRACTICE)

    def select_search_area_ccg(self)->None:
        self.select_area.select_option(self.SEARCH_AREA_CCG)

    def select_search_area_screening_centre(self)->None:
        self.select_area.select_option(self.SEARCH_AREA_SCREENING_CENTRE)

    def select_search_area_other_hub(self)->None:
        self.select_area.select_option(self.SEARCH_AREA_OTHER_HUB)

    def select_search_area_whole_database(self)->None:
        self.select_area.select_option(self.SEARCH_AREA_WHOLE_DATABASE)
