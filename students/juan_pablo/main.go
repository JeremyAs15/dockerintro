package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"time"
)

const (
	defaultStudent = "Juan Pablo"
	defaultBarrio  = "Colseguros"
	logPath        = "/var/log/app/visitas.log"
)

type service struct {
	student string
	barrio  string
	logFile string
	mu      sync.Mutex
}

type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (w *statusRecorder) WriteHeader(status int) {
	w.status = status
	w.ResponseWriter.WriteHeader(status)
}

func envOrDefault(name, fallback string) string {
	if value := os.Getenv(name); value != "" {
		return value
	}
	return fallback
}

func newService() *service {
	return &service{
		student: envOrDefault("STUDENT_NAME", defaultStudent),
		barrio:  envOrDefault("BARRIO", defaultBarrio),
		logFile: logPath,
	}
}

func (s *service) routes() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/", s.handleRoot)
	mux.HandleFunc("/health", s.handleHealth)
	return s.withRequestLogging(mux)
}

func (s *service) handleRoot(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	_, _ = fmt.Fprintf(w, "Hola, I am %s and I live in %s", s.student, s.barrio)
}

func (s *service) handleHealth(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte(`{"ok": true}`))
}

func (s *service) withRequestLogging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		recorder := &statusRecorder{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(recorder, r)
		s.logRequest(r, recorder.status)
	})
}

func (s *service) logRequest(r *http.Request, status int) {
	line := fmt.Sprintf("%s method=%s path=%s status=%d\n", time.Now().UTC().Format(time.RFC3339), r.Method, r.URL.Path, status)

	s.mu.Lock()
	defer s.mu.Unlock()

	file, err := os.OpenFile(s.logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		log.Printf("unable to write visit log: %v", err)
		return
	}
	defer file.Close()

	_, _ = file.WriteString(line)
}

func main() {
	svc := newService()
	if err := os.MkdirAll(filepath.Dir(svc.logFile), 0o755); err != nil {
		log.Printf("unable to create log directory: %v", err)
	}

	server := &http.Server{
		Addr:    ":8080",
		Handler: svc.routes(),
	}

	log.Fatal(server.ListenAndServe())
}
