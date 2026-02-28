package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
)

const appName = "claude-desktop-proxy"

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	switch os.Args[1] {
	case "open":
		n := 1
		if len(os.Args) >= 3 {
			var err error
			n, err = strconv.Atoi(os.Args[2])
			if err != nil || n < 1 {
				fmt.Fprintf(os.Stderr, "Error: count must be a positive integer\n")
				os.Exit(1)
			}
		}
		openWindows(n)
	case "list":
		listProfiles()
	case "clean":
		cleanProfiles()
	case "path":
		if len(os.Args) < 3 {
			fmt.Fprintf(os.Stderr, "Error: provide the path to Claude Desktop binary\n")
			fmt.Fprintf(os.Stderr, "Usage: %s path /full/path/to/claude\n", appName)
			os.Exit(1)
		}
		setCustomPath(os.Args[2])
	default:
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Printf(`%s - Run multiple Claude Desktop windows

Usage:
  %s open [count]   Open new Claude Desktop window(s) (default: 1)
  %s list           List existing profiles
  %s clean          Remove all extra profiles
  %s path <binary>  Set custom path to Claude Desktop binary

Examples:
  %s open           Open one new window
  %s open 3         Open three new windows
  %s clean          Delete all extra profile directories
`, appName, appName, appName, appName, appName, appName, appName, appName)
}

// profilesDir returns the base directory where extra profiles are stored.
func profilesDir() string {
	dir, err := os.UserConfigDir()
	if err != nil {
		dir = os.TempDir()
	}
	return filepath.Join(dir, appName, "profiles")
}

// configDir returns the app config directory.
func configDir() string {
	dir, err := os.UserConfigDir()
	if err != nil {
		dir = os.TempDir()
	}
	return filepath.Join(dir, appName)
}

// customPathFile returns the file where a custom binary path is stored.
func customPathFile() string {
	return filepath.Join(configDir(), "binary-path")
}

func setCustomPath(p string) {
	dir := configDir()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		fmt.Fprintf(os.Stderr, "Error creating config dir: %v\n", err)
		os.Exit(1)
	}
	if err := os.WriteFile(customPathFile(), []byte(p), 0o644); err != nil {
		fmt.Fprintf(os.Stderr, "Error saving path: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Claude Desktop binary path set to: %s\n", p)
}

func getCustomPath() string {
	data, err := os.ReadFile(customPathFile())
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(data))
}

// findClaude locates the Claude Desktop binary.
func findClaude() (string, error) {
	// Check custom path first.
	if p := getCustomPath(); p != "" {
		if _, err := os.Stat(p); err == nil {
			return p, nil
		}
	}

	// Platform-specific default locations.
	var candidates []string
	switch runtime.GOOS {
	case "darwin":
		candidates = []string{
			"/Applications/Claude.app/Contents/MacOS/Claude",
		}
	case "windows":
		localAppData := os.Getenv("LOCALAPPDATA")
		if localAppData != "" {
			candidates = append(candidates, filepath.Join(localAppData, "Programs", "Claude", "Claude.exe"))
		}
		candidates = append(candidates, `C:\Program Files\Claude\Claude.exe`)
	case "linux":
		candidates = []string{
			"/usr/bin/claude-desktop",
			"/usr/local/bin/claude-desktop",
			"/opt/Claude/claude-desktop",
			"/snap/claude-desktop/current/claude-desktop",
		}
		// Also check flatpak.
		home, _ := os.UserHomeDir()
		if home != "" {
			candidates = append(candidates, filepath.Join(home, ".local/bin/claude-desktop"))
		}
	}

	for _, c := range candidates {
		if _, err := os.Stat(c); err == nil {
			return c, nil
		}
	}

	// Fall back to PATH lookup.
	for _, name := range []string{"claude-desktop", "Claude", "claude"} {
		if p, err := exec.LookPath(name); err == nil {
			return p, nil
		}
	}

	return "", fmt.Errorf("Claude Desktop not found. Set it manually:\n  %s path /full/path/to/claude", appName)
}

// nextProfileDir returns the next available profile directory.
func nextProfileDir() string {
	base := profilesDir()
	for i := 1; ; i++ {
		dir := filepath.Join(base, fmt.Sprintf("window-%d", i))
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			return dir
		}
	}
}

func openWindows(count int) {
	claudePath, err := findClaude()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Using Claude Desktop at: %s\n", claudePath)

	for i := 0; i < count; i++ {
		profileDir := nextProfileDir()
		if err := os.MkdirAll(profileDir, 0o755); err != nil {
			fmt.Fprintf(os.Stderr, "Error creating profile dir: %v\n", err)
			os.Exit(1)
		}

		cmd := exec.Command(claudePath, "--user-data-dir="+profileDir)
		cmd.Stdout = nil
		cmd.Stderr = nil
		if err := cmd.Start(); err != nil {
			fmt.Fprintf(os.Stderr, "Error launching window: %v\n", err)
			os.Exit(1)
		}

		// Detach — don't wait for the process.
		go cmd.Wait()

		fmt.Printf("Opened window %d (profile: %s)\n", i+1, filepath.Base(profileDir))
	}
}

func listProfiles() {
	base := profilesDir()
	entries, err := os.ReadDir(base)
	if err != nil {
		if os.IsNotExist(err) {
			fmt.Println("No profiles yet. Run: " + appName + " open")
			return
		}
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	if len(entries) == 0 {
		fmt.Println("No profiles yet. Run: " + appName + " open")
		return
	}

	fmt.Printf("Profiles in %s:\n\n", base)
	for _, e := range entries {
		if e.IsDir() {
			fmt.Printf("  %s\n", e.Name())
		}
	}
}

func cleanProfiles() {
	base := profilesDir()
	if _, err := os.Stat(base); os.IsNotExist(err) {
		fmt.Println("Nothing to clean.")
		return
	}

	if err := os.RemoveAll(base); err != nil {
		fmt.Fprintf(os.Stderr, "Error cleaning profiles: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("All extra profiles removed.")
}
