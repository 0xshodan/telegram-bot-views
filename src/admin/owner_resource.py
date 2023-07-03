from fastapi_admin.resources import Model
from starlette.datastructures import FormData

from tortoise.queryset import QuerySet

from starlette.requests import Request


class OwnerResource(Model):
    @classmethod
    async def resolve_query_params(cls, request: Request, values: dict, qs: QuerySet):
        qs = qs.filter(owner=request.state.admin)
        return await super().resolve_query_params(request, values, qs)

    @classmethod
    async def resolve_data(cls, request: Request, data: FormData):
        ret, m2m_ret = await super().resolve_data(request, data)
        ret["owner"] = request.state.admin
        return ret, m2m_ret
