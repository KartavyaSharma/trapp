import constants.constants as constants
import datetime
import pandas as pd

from . import status


class Entry:
    def __init__(self,
                 company: str,
                 position: str,
                 date_applied: datetime.datetime,
                 status: status.Status,
                 link: str,
                 notes: str
                 ):
        self.company = company
        self.position = position
        self.date_applied = date_applied
        self.status = status
        self.link = link
        self.notes = notes

    def create_dataframe(self) -> pd.DataFrame:
        self.validate()
        df_dict = {key: None for key in constants.COLUMN_NAMES}
        df_dict["Company"] = self.company
        df_dict["Position"] = self.position
        df_dict["Date Applied"] = self.date_applied
        df_dict["Status"] = self.status
        df_dict["Portal Link"] = self.link
        df_dict["Notes"] = self.notes
        df = pd.DataFrame(df_dict, index=[0])
        return df

    def validate(self):
        assert self.status in status.Status
        self.status = self.status.value
        try:
            self.date_applied = datetime.datetime.strftime(
                self.date_applied, "%m/%d/%Y"
            )
        except Exception as e:
            print(e)
            return
        assert self.company is not None
        assert self.position is not None
        assert self.link is not None
