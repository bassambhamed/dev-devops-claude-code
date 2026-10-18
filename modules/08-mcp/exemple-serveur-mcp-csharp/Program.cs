using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

var builder = Host.CreateApplicationBuilder(args);

// stdio : stdout est réservé au protocole MCP (JSON-RPC) → les logs DOIVENT aller sur stderr.
builder.Logging.AddConsole(o => o.LogToStandardErrorThreshold = LogLevel.Trace);

// HttpClient vers l'API Catalog (URL surchargeable par variable d'environnement).
builder.Services.AddSingleton(_ =>
{
    var baseUrl = Environment.GetEnvironmentVariable("CATALOG_API_URL") ?? "http://localhost:5147";
    return new HttpClient { BaseAddress = new Uri(baseUrl) };
});

builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();   // découvre toutes les classes marquées [McpServerToolType]

await builder.Build().RunAsync();
