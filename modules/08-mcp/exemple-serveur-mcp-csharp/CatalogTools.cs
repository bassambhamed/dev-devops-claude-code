using System.ComponentModel;
using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using ModelContextProtocol.Server;

namespace ECommerce.Catalog.McpServer;

// Les outils exposés au modèle. Une méthode = un outil ; la [Description] est ce que le
// modèle lit pour décider QUAND l'appeler : c'est de la conception d'API, pour un modèle.
//
// Serveur volontairement en LECTURE SEULE : aucun outil n'écrit dans le catalogue.
// Un outil d'écriture ne s'ajoute qu'avec une raison impérieuse, une revue, et un
// rôle technique côté API qui le limite.
[McpServerToolType]
public static class CatalogTools
{
    [McpServerTool(Name = "list_products")]
    [Description("Liste tous les produits du catalogue e-commerce (id, nom, prix, stock).")]
    public static async Task<string> ListProducts(HttpClient http)
        => await http.GetStringAsync("/api/products");

    [McpServerTool(Name = "get_product")]
    [Description("Récupère un produit du catalogue par son identifiant numérique.")]
    public static async Task<string> GetProduct(
        HttpClient http,
        [Description("Identifiant du produit")] int id)
    {
        var response = await http.GetAsync($"/api/products/{id}");
        return response.StatusCode == HttpStatusCode.NotFound
            ? $"Aucun produit avec l'id {id}."
            : await response.Content.ReadAsStringAsync();
    }

    // La valeur ajoutée d'un serveur MCP : un outil peut porter une logique métier qui
    // n'existe pas dans l'API, au lieu d'être un simple miroir de ses routes.
    [McpServerTool(Name = "low_stock_products")]
    [Description("Liste les produits dont le stock est sous un seuil — utile pour préparer un réassort.")]
    public static async Task<string> LowStockProducts(
        HttpClient http,
        [Description("Seuil de stock (10 par défaut)")] int threshold = 10)
    {
        var products = await http.GetFromJsonAsync<List<ProductDto>>("/api/products") ?? [];
        var low = products.Where(p => p.AvailableStock < threshold).ToList();
        return low.Count == 0
            ? $"Aucun produit sous le seuil de {threshold}."
            : JsonSerializer.Serialize(low, JsonSerializerOptions.Web);
    }

    private sealed record ProductDto(int Id, string Name, string? Description, decimal Price, int AvailableStock);
}
