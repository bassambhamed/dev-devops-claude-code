namespace ECommerce.Web.Services;

/// <summary>
/// Talks to the Catalog service through the gateway ("/catalog/...").
/// Base address is resolved by Aspire service discovery.
/// </summary>
public class CatalogApiClient(HttpClient httpClient)
{
    public async Task<IReadOnlyList<ProductDto>> GetProductsAsync(
        int? categoryId = null, string? search = null, CancellationToken ct = default)
    {
        var query = new List<string>();
        if (categoryId is not null) query.Add($"categoryId={categoryId}");
        if (!string.IsNullOrWhiteSpace(search)) query.Add($"search={Uri.EscapeDataString(search.Trim())}");

        var url = "/catalog/api/products" + (query.Count > 0 ? "?" + string.Join('&', query) : "");
        return await httpClient.GetFromJsonAsync<List<ProductDto>>(url, ct) ?? [];
    }

    public async Task<IReadOnlyList<CategoryDto>> GetCategoriesAsync(CancellationToken ct = default) =>
        await httpClient.GetFromJsonAsync<List<CategoryDto>>("/catalog/api/categories", ct) ?? [];
}

public record ProductDto(int Id, string Sku, string Name, string? Description, decimal Price, int AvailableStock, int CategoryId);
public record CategoryDto(int Id, string Name);
