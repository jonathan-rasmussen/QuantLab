class TechnicalAnalysis:
    def __init__(self):
        pass

    def hammer_detect(self, bar):
        body_size = abs(bar["open"] - bar["close"])

        # Red Hammer
        if bar["open"] > bar["close"]:
            lower_wick = abs(bar["close"] - bar["low"])
            upper_wick = abs(bar["high"] - bar["open"])

        # Green hammer
        else:
            lower_wick = abs(bar["open"] - bar["low"])
            upper_wick = abs(bar["high"] - bar["close"])

        is_hammer = lower_wick >= body_size and upper_wick < body_size * 0.25
        is_inverted_hammer = upper_wick >= body_size and lower_wick < body_size * 0.25

        return is_hammer or is_inverted_hammer
