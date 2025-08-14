# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.

from typing import List

from alibabacloud_dingtalk.oauth2_1_0 import models as dingtalkoauth_2__1__0_models
from alibabacloud_dingtalk.oauth2_1_0.client import Client as dingtalkoauth2_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util.client import Client as UtilClient


class Oauth:
    def __init__(self, app_key: str, app_secret: str) -> None:
        self.app_key = app_key
        self.app_secret = app_secret
        self.client = Oauth.create_client()

    @staticmethod
    def create_client() -> dingtalkoauth2_1_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkoauth2_1_0Client(config)

    def main(self):
        get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
            app_key=self.app_key,
            app_secret=self.app_secret
        )
        try:
            resp = self.client.get_access_token(get_access_token_request)
            return resp.body.to_map()
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                pass
            print(err)

    @staticmethod
    async def main_async(
            args: List[str],
    ) -> None:
        client = Oauth.create_client()
        get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
            app_key='dingeqqpkv3xxxxxx',
            app_secret='GT-lsu-taDAxxxsTsxxxx'
        )
        try:
            await client.get_access_token_async(get_access_token_request)
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                pass


if __name__ == '__main__':
    oauth = Oauth(
        app_key=config.get('dingtalk.app_key'),
        app_secret=config.get('dingtalk.app_secret')
    )
    resp = oauth.main()
    print(resp)
