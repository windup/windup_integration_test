from mta.entities.analysis_results import AnalysisResults
from mta.entities.analysis_results import AnalysisResultsView


def test_analysis_results_search_sort_delete(application, create_project):
    """ Validates Web console Test 03
    1) Upload more than one application into a project to analyse
    2) Search analysis
    3) Delete analysis
    """
    project, project_collection = create_project
    assert project.exists

    analysis_results = AnalysisResults(application, project.name)
    analysis_results.run_analysis()
    view = analysis_results.create_view(AnalysisResultsView)

    # search row 1 in list
    analysis_results.search_analysis(row=1)
    assert view.analysis_row(row=1).analysis_number.is_displayed
    view.clear_search()
    # search row 2 in list
    analysis_results.search_analysis(row=2)
    view.clear_search()
    # Sort Analysis
    analysis_results.sort_analysis()
    assert analysis_results.get_analysis_number(view, row=1) > analysis_results.get_analysis_number(
        view, row=2
    )

    # delete analysis of row 1 and cancel
    analysis_results.delete_analysis(row=1)
    view.cancel_delete.wait_displayed()
    view.cancel_delete.click()
    # delete analysis of row 1 and confirm
    view.wait_displayed()
    analysis_results.delete_analysis(row=1)
    view.confirm_delete.wait_displayed()
    view.confirm_delete.click()
