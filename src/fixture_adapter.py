from mock_upcoming import load_mock_upcoming


def load_fixtures(source="mock", **kwargs):
    """
    Returns:
      {
        "fixtures": DataFrame,
        "models": {
            "1x2": model,
            "btts": model,
            "ou25": model
        }
      }
    """

    if source == "mock":
        return load_mock_upcoming(**kwargs)

    raise ValueError(f"Unknown fixture source: {source}")
