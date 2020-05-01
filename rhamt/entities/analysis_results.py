from widgetastic.widget import Text
from widgetastic_patternfly import Button

from rhamt.entities import BaseLoggedInPage
from rhamt.widgetastic import AnalysisResults


class AnalysisResultsView(BaseLoggedInPage):

    run_analysis_button = Button("Run Analysis")
    title = Text(locator=".//div/h2[normalize-space(.)='Active Analysis']")
    analysis_results = AnalysisResults()

    @property
    def is_displayed(self):
        return self.run_analysis_button.is_displayed and self.title.is_displayed
