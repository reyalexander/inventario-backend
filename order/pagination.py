from rest_framework.pagination import PageNumberPagination

class OrderPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response['total_price'] = self.paginator.count
        return response