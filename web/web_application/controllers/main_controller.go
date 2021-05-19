package main

import (
    "github.com/beego/beego/v2/server/web"
)

type MainController struct {
    web.Controller
}

func (this *MainController) ShowHomepage() {
    this.Ctx.WriteString("Home Page")
}
