import pandas as pd
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.decorators import login_required
import tempfile

@login_required
def upload_and_process(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # Save file temporarily in memory (not in media/)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        temp_file.write(file.read())
        temp_file.close()  # Close so we can reopen it later

        file_path = temp_file.name  # Store temporary path
        request.session['file_path'] = file_path  # Save path in session

        # Read available sheets
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            return JsonResponse({'sheets': sheets})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'POST' and request.POST.get('selected_sheet'):
        selected_sheet = request.POST.get('selected_sheet')
        file_path = request.session.get('file_path')

        if not file_path:
            return JsonResponse({'error': 'File not found. Try re-uploading it.'}, status=400)

        try:
            df = pd.read_excel(file_path, sheet_name=selected_sheet)
            columns = df.columns.tolist()
            request.session['df_columns'] = columns
            request.session['selected_sheet'] = selected_sheet
            return JsonResponse({'columns': columns})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'dashboard/manage_data.html')
