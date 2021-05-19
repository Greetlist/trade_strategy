package routers

import (
    "github.com/beego/beego/v2/server/web"
    "controller"
)

func init() {
    web.Router("/", &controller.MainController{}, "Get:ShowHomePage")
}
