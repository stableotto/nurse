from jobspy.model import Compensation, CompensationInterval, Location, JobType


def parse_compensation(data: dict) -> Compensation | None:
    pay_period = data.get("payPeriod")
    adjusted_pay = data.get("payPeriodAdjustedPay")
    currency = data.get("payCurrency", "USD")
    if not pay_period or not adjusted_pay:
        return None

    interval = None
    if pay_period == "ANNUAL":
        interval = CompensationInterval.YEARLY
    elif pay_period:
        interval = CompensationInterval.get_interval(pay_period)
    min_amount = int(adjusted_pay.get("p10") // 1)
    max_amount = int(adjusted_pay.get("p90") // 1)
    return Compensation(
        interval=interval,
        min_amount=min_amount,
        max_amount=max_amount,
        currency=currency,
    )


def get_job_type_enum(job_type_str: str) -> list[JobType] | None:
    for job_type in JobType:
        if job_type_str in job_type.value:
            return [job_type]


def parse_location(location_name: str) -> Location | None:
    if not location_name or location_name == "Remote":
        return
    city, _, state = location_name.partition(", ")
    return Location(city=city, state=state)


def get_cursor_for_page(pagination_cursors, page_num):
    for cursor_data in pagination_cursors:
        if cursor_data["pageNumber"] == page_num:
            return cursor_data["cursor"]
