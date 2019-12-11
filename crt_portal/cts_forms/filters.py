# Class to handle filtering Reports by supplied query params,
# provided they are valid filterable model properties.


class ReportFilter:
    def __init__(self, model, filter_dict):
        self.model = model
        self.filterable_fields = ['assigned_section']
        self.filters = self.__sanitize_filters(filter_dict)

    # Populate internal filters object with valid filterable fields
    def __sanitize_filters(self, filter_dict):
        filters = {}

        for field in self.filterable_fields:
            if field in filter_dict:
                filters.update({
                    field: filter_dict[field]
                })

        return filters

    def get_filters(self):
        return self.filters

    # Return a QuerySet ready to be filtered on evaluation, or the
    # original QuerySet supplied to this class on instantiation
    def filter(self):
        filtered = self.model.objects
        filters = self.get_filters()

        if len(filters.keys()):
            filtered = filtered.filter(**filters)

        return filtered
