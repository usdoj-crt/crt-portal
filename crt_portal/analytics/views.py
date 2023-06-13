from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from .admin import Notebook


class RefreshNotebookView(generics.RetrieveAPIView):
    """
    A view that refreshes a notebook cell.

    For example, to refresh cell 1 of notebook 0:
        /analytics/notebooks/refresh/1/0
    """
    queryset = Notebook.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            run_only_cell = int(request.GET['run_only_cell'])
        except KeyError:
            run_only_cell = None
        notebook = self.get_object()
        next_cell = notebook.refresh(run_only_cell=run_only_cell)
        notebook.save()
        return Response({'next_cell': next_cell})
