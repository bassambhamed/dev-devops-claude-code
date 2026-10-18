using ECommerce.Catalog.Api.Data;
using ECommerce.Catalog.Api.Endpoints;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Aspire: telemetry, health checks, resilience, service discovery.
builder.AddServiceDefaults();

builder.Services.AddOpenApi();

// PostgreSQL through Aspire: the connection string "catalogdb" is injected by the AppHost
// (ConnectionStrings__catalogdb). This also adds a database health check (readiness)
// and EF Core / Npgsql traces and metrics to OpenTelemetry.
builder.AddNpgsqlDbContext<CatalogDbContext>("catalogdb");

var app = builder.Build();

// Aspire default endpoints (/health, /alive).
app.MapDefaultEndpoints();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();

    // Development only: apply pending migrations at startup. In shared environments,
    // migrations run as a reviewed, explicit step (CI job or Kubernetes Job), never here.
    using var scope = app.Services.CreateScope();
    var db = scope.ServiceProvider.GetRequiredService<CatalogDbContext>();
    db.Database.Migrate();
}

app.MapCatalogEndpoints();

app.Run();

// Makes the Program class visible to the integration tests (WebApplicationFactory<Program>).
public partial class Program { }
