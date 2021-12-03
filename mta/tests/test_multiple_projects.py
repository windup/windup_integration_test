"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
import fauxfactory
import pytest

from mta.entities.analysis_results import AnalysisResults
from mta.entities.applications import Applications


@pytest.mark.skip(reason="MTA UI Issue - WINDUP-3160")
def test_multiple_applications_upload(mta_app, request):
    """Test multiple applications upload

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project
            2. While creating project browse multiple applications files
            3. Go to applications page and delete one application
            4. Run the analysis
        expectedResults:
            1. Analysis should get complete properly
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = mta_app.collections.projects
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=[
            "acmeair-webapp-1.0-SNAPSHOT.war",
            "arit-ear-0.8.1-SNAPSHOT.ear",
            "cadmium-war-0.1.0.war",
        ],
        transformation_path="Containerization",
    )
    applications = Applications(mta_app, project_name)
    applications.delete_application("arit-ear-0.8.1-SNAPSHOT.ear")
    # Verify that analysis completes
    analysis = AnalysisResults(mta_app, project_name)
    analysis.run_analysis()

    @request.addfinalizer
    def _finalize():
        project.delete()
