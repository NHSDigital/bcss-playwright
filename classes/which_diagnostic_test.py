class WhichDiagnosticTest:
    """
    Maps descriptive diagnostic test selection types to internal constants.
    Used to determine join and filter behavior in the query builder.
    """

    ANY_TEST_IN_ANY_EPISODE = "any_test_in_any_episode"
    ANY_TEST_IN_LATEST_EPISODE = "any_test_in_latest_episode"
    ONLY_TEST_IN_LATEST_EPISODE = "only_test_in_latest_episode"
    ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE = "only_not_void_test_in_latest_episode"
    LATEST_TEST_IN_LATEST_EPISODE = "latest_test_in_latest_episode"
    LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE = "latest_not_void_test_in_latest_episode"
    EARLIEST_NOT_VOID_TEST_IN_LATEST_EPISODE = (
        "earliest_not_void_test_in_latest_episode"
    )
    EARLIER_TEST_IN_LATEST_EPISODE = "earlier_test_in_latest_episode"
    LATER_TEST_IN_LATEST_EPISODE = "later_test_in_latest_episode"

    _valid_values = {
        ANY_TEST_IN_ANY_EPISODE,
        ANY_TEST_IN_LATEST_EPISODE,
        ONLY_TEST_IN_LATEST_EPISODE,
        ONLY_NOT_VOID_TEST_IN_LATEST_EPISODE,
        LATEST_TEST_IN_LATEST_EPISODE,
        LATEST_NOT_VOID_TEST_IN_LATEST_EPISODE,
        EARLIEST_NOT_VOID_TEST_IN_LATEST_EPISODE,
        EARLIER_TEST_IN_LATEST_EPISODE,
        LATER_TEST_IN_LATEST_EPISODE,
    }

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._valid_values:
            raise ValueError(f"Unknown diagnostic test selection: '{description}'")
        return key
