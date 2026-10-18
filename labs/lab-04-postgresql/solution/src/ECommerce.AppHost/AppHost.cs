var builder = DistributedApplication.CreateBuilder(args);

// PostgreSQL server (Docker container started by Aspire) + the Catalog database.
// - Fixed host port 5433: tools outside Aspire (psql, the DBHub MCP server) always find it.
// - Data volume: data survives an AppHost restart (unlike the former in-memory provider).
// - The superuser password is an Aspire parameter: generated and stored in the AppHost
//   user secrets, never written in this file.
var postgres = builder.AddPostgres("postgres", port: 5433)
    .WithDataVolume("ecommerce-pgdata");

var catalogDb = postgres.AddDatabase("catalogdb");

// Catalog microservice — now backed by PostgreSQL.
var catalog = builder.AddProject<Projects.ECommerce_Catalog_Api>("catalog")
    .WithReference(catalogDb)
    .WaitFor(catalogDb);

// Ordering microservice — depends on Catalog (resolved via service discovery).
var ordering = builder.AddProject<Projects.ECommerce_Ordering_Api>("ordering")
    .WithReference(catalog)
    .WaitFor(catalog);

// API Gateway (YARP) — the single entry point for the services.
var gateway = builder.AddProject<Projects.ECommerce_Gateway>("gateway")
    .WithReference(catalog)
    .WithReference(ordering)
    .WaitFor(catalog)
    .WaitFor(ordering);

// Blazor web frontend — talks to the services through the gateway.
builder.AddProject<Projects.ECommerce_Web>("web")
    .WithReference(gateway)
    .WaitFor(gateway)
    .WithExternalHttpEndpoints();

builder.Build().Run();
