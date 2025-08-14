# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.

from typing import List

from alibabacloud_dingtalk.doc_1_0 import models as dingtalkdoc__1__0_models
from alibabacloud_dingtalk.doc_1_0.client import Client as dingtalkdoc_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class ReadSheet:
    def __init__(self):
        self.client = ReadSheet.create_client()

    @staticmethod
    def create_client() -> dingtalkdoc_1_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkdoc_1_0Client(config)

    def main(self, token, union_id, workbook_id, sheet_id, range_address):
        get_range_headers = dingtalkdoc__1__0_models.GetRangeHeaders()
        get_range_headers.x_acs_dingtalk_access_token = token
        get_range_request = dingtalkdoc__1__0_models.GetRangeRequest(
            select='values',
            operator_id=union_id
        )
        try:
            resp = self.client.get_range_with_options(workbook_id, sheet_id, range_address,
                                                      get_range_request, get_range_headers,
                                                      util_models.RuntimeOptions())
            return resp.body.to_map()
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                pass
            print(err)
            return None

    @staticmethod
    async def main_async(
            args: List[str],
    ) -> None:
        client = ReadSheet.create_client()
        get_range_headers = dingtalkdoc__1__0_models.GetRangeHeaders()
        get_range_headers.x_acs_dingtalk_access_token = '<your access token>'
        get_range_request = dingtalkdoc__1__0_models.GetRangeRequest(
            select='values',
            operator_id='ppgAxxx'
        )
        try:
            await client.get_range_with_options_async('e54Lq3xxx', 'Sheet1', 'A1:B2', get_range_request,
                                                      get_range_headers, util_models.RuntimeOptions())
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                pass
