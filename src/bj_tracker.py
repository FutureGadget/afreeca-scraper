import pytz
from datetime import datetime, timezone
import gmail

KST = pytz.timezone("Asia/Seoul")


def get_now_as_kst():
    utc_dt = datetime.now(timezone.utc)
    return utc_dt.astimezone(tz=KST)


def is_same_date_in_kst(dt: datetime):
    if not dt:
        return False
    else:
        now = get_now_as_kst()
        return now.year == dt.year and \
               now.month == dt.month and \
               now.day == dt.day


class ShineeTracker:
    last_live_date = None

    def __init__(self, start_tomorrow=True):
        if start_tomorrow:
            ShineeTracker.last_live_date = datetime.now(timezone.utc)
        else:
            ShineeTracker.last_live_date = None
        self.last_email_sent = None
        self.shinee_usual_broadcast_finish_hour_with_buffer_in_kst = 16

    def today_live_datetime_in_kst(self):
        if ShineeTracker.last_live_date:
            return ShineeTracker.last_live_date.astimezone(tz=KST)
        return None

    @staticmethod
    def broadcast_started():
        ShineeTracker.last_live_date = datetime.now(timezone.utc)

    def had_live_today(self):
        now = get_now_as_kst()
        livetime = self.today_live_datetime_in_kst()
        return livetime is not None and \
               livetime.year == now.year and \
               livetime.month == now.month and \
               livetime.day == now.day

    def should_send_email(self):
        now = get_now_as_kst()
        return not self.had_live_today() and \
               now.hour >= self.shinee_usual_broadcast_finish_hour_with_buffer_in_kst and \
               not is_same_date_in_kst(self.last_email_sent)

    def send_email_if_had_no_live_today(self):
        if self.should_send_email():
            gmail.broadcast_to_enrolled_users(
                subject='샤교수 스타강의는 오늘 휴강으로 보인다.',
                message_text='이 메일은 오후 4시가 지났는데 오늘의 샤교수 강의가 시작되지 않았으면 발송되는 메일이다.\n\
                    샤튜브 주소: https://www.youtube.com/channel/UCJNTwhCAZX6hJkbUB4TKdZQ\n\
                    샤녹방 주소: https://studio.youtube.com/channel/UCWif_OFSioIKFLDka9PmXRg/videos/upload'
            )
            self.last_email_sent = get_now_as_kst()


if __name__ == '__main__':
    tracker = ShineeTracker(start_tomorrow=False)
    print(f'Today live datytime in kst: {tracker.today_live_datetime_in_kst()}')
    # print(f'live today {tracker.had_live_today()}')
    print(f'should send email: {tracker.should_send_email()}')
    tracker.send_email_if_had_no_live_today()
    print(f'should send email after sent: {tracker.should_send_email()}')
