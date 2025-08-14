# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.

from typing import List

from alibabacloud_dingtalk.doc_1_0 import models as dingtalkdoc__1__0_models
from alibabacloud_dingtalk.doc_1_0.client import Client as dingtalkdoc_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class WriteSheet:
    def __init__(self):
        self.client = WriteSheet.create_client()

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

    def main(self, token, union_id, values, workbook_id, sheet_id, range_address) -> None:
        update_range_headers = dingtalkdoc__1__0_models.UpdateRangeHeaders()
        update_range_headers.x_acs_dingtalk_access_token = token
        update_range_request = dingtalkdoc__1__0_models.UpdateRangeRequest(
            operator_id=union_id,
            values=values
        )
        try:
            self.client.update_range_with_options(workbook_id, sheet_id, range_address,
                                                  update_range_request, update_range_headers,
                                                  util_models.RuntimeOptions())
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                pass
            print(err)

    @staticmethod
    async def main_async(
            args: List[str],
    ) -> None:
        client = WriteSheet.create_client()
        update_range_headers = dingtalkdoc__1__0_models.UpdateRangeHeaders()
        update_range_headers.x_acs_dingtalk_access_token = '<your access token>'
        update_range_request = dingtalkdoc__1__0_models.UpdateRangeRequest(
            operator_id='ppgAQuxxxxx',
            values=[
                [
                    'text'
                ]
            ],
            background_colors=[
                [
                    '#ff0000'
                ]
            ],
            hyperlinks=[
                [
                    None
                ]
            ],
            number_format='@'
        )
        try:
            await client.update_range_with_options_async('e54Lqxxxxx', 'Sheet1', 'A1:B1', update_range_request,
                                                         update_range_headers, util_models.RuntimeOptions())
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                pass
