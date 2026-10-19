package main

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRootUsesEnvironmentValues(t *testing.T) {
	t.Setenv("STUDENT_NAME", "Juan Pablo")
	t.Setenv("BARRIO", "Colseguros")

	svc := newService()
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	res := httptest.NewRecorder()

	svc.routes().ServeHTTP(res, req)

	if res.Code != http.StatusOK {
		t.Fatalf("expected status %d, got %d", http.StatusOK, res.Code)
	}

	want := "Hola, I am Juan Pablo and I live in Colseguros"
	if strings.TrimSpace(res.Body.String()) != want {
		t.Fatalf("expected %q, got %q", want, res.Body.String())
	}
}

func TestHealthEndpoint(t *testing.T) {
	svc := newService()
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	res := httptest.NewRecorder()

	svc.routes().ServeHTTP(res, req)

	if res.Code != http.StatusOK {
		t.Fatalf("expected status %d, got %d", http.StatusOK, res.Code)
	}

	if strings.TrimSpace(res.Body.String()) != `{"ok": true}` {
		t.Fatalf("unexpected body: %q", res.Body.String())
	}
}

func TestRequestLoggingWritesVisitLog(t *testing.T) {
	logFile := filepath.Join(t.TempDir(), "visitas.log")
	svc := &service{student: "Juan Pablo", barrio: "Colseguros", logFile: logFile}

	req := httptest.NewRequest(http.MethodGet, "/", nil)
	res := httptest.NewRecorder()
	svc.routes().ServeHTTP(res, req)

	content, err := os.ReadFile(logFile)
	if err != nil {
		t.Fatalf("expected log file to exist: %v", err)
	}

	line := string(content)
	if !strings.Contains(line, "method=GET") || !strings.Contains(line, "path=/") || !strings.Contains(line, "status=200") {
		t.Fatalf("unexpected log line: %q", line)
	}
}
