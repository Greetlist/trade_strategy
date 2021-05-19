package main

import (
    "github.com/spf13/cobra"
    "fmt"
    "os"
    "server"
)

var (
    bindAddr string
    bindPort int
)

var rootCmd = &cobra.Command {
    Use: "Statistic Web",
    Short: "Statistic Web show Stock data automatic",
    Run: func (cmd *cobra.Command, args []string) error {
        server.RunServer()
    }
}

func init() {
    rootCmd.PersistentFlags().StringVarP(&bindAddr, "bind_addr", "0.0.0.0", "server bind interface")
    rootCmd.PersistentFlags().IntVarP(&bindPort, "bind_port", "8080", "server bind port")
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Printf("root cmd execute error.\n")
        os.Exit(1)
    }
}

func main() {
    Execute()
}
