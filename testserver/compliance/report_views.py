from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin, xframe_options_exempt

from .src.assets import AssetListAction, AssetTableAction, AssetFileAction, AssetDataAction
from .src.evidence import EvidenceDataList, EvidenceDataHandler, EvidenceFileHandler, ComplianceHandler
from .src.lists import ComplianceFileHandler, ComplianceListHandler
from .src.policy import CompliancePolicyHandler, PolicyFileHandler
from .src.file import get_file_preivew_details

from .models import Evidence, Asset, Policy

@login_required
def index_report(request, compliance_type):
    data = {
        'report_type': compliance_type
    }
    
    return render(request, f"report/index.html", data)

class RenderCompliance:
    def __init__(self, request) -> None:
        self.request = request