class AuditViewMixin:
    """
    Agrega created_by y updated_by automáticamente.
    Para usarlo, heredar antes que CreateView/UpdateView.
    """

    def form_valid(self, form):
        obj = form.save(commit=False)

        if not obj.pk:
            obj.created_by = self.request.user

        obj.updated_by = self.request.user
        
        obj.save()
        return super().form_valid(form)
