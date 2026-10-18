using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace ECommerce.Catalog.Api.Data;

// Used ONLY by `dotnet ef` at design time, to build the model outside Aspire.
// At runtime the real connection string comes from Aspire (resource "catalogdb").
//
// `dotnet ef migrations add` never opens a connection, so this string carries no
// credentials at all. `dotnet ef database update` would need one: pass it explicitly
// with --connection "$CATALOG_DB_CONNECTION" instead of writing it here.
public class CatalogDbContextFactory : IDesignTimeDbContextFactory<CatalogDbContext>
{
    public CatalogDbContext CreateDbContext(string[] args)
    {
        var options = new DbContextOptionsBuilder<CatalogDbContext>()
            .UseNpgsql("Host=localhost;Port=5433;Database=catalogdb")
            .Options;

        return new CatalogDbContext(options);
    }
}
