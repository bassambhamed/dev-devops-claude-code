// Test de CONTRAT du Catalog, ajouté après l'incident du lab 11 (scénario A).
//
// Les tests de chaque service étaient verts : Catalog se relisait avec sa propre classe,
// Ordering parlait à un faux Catalog. Personne ne vérifiait ce que les CONSOMMATEURS
// (Ordering, Web) attendent : un champ JSON nommé `price`. Ce test lit le JSON brut, sans
// passer par le modèle C#, et fige ce contrat.
using System.Text.Json;
using Xunit;

namespace ECommerce.Catalog.Tests;

public class CatalogContractTests(CatalogApiFactory factory) : IClassFixture<CatalogApiFactory>
{
    private readonly HttpClient _client = factory.CreateClient();

    [Theory]
    [InlineData("id")]
    [InlineData("name")]
    [InlineData("price")]            // lu par Ordering (CatalogProduct) et par Web (ProductDto)
    [InlineData("availableStock")]
    public async Task GetProductById_ExposeLesChampsAttendusParLesConsommateurs(string champ)
    {
        using var json = JsonDocument.Parse(await _client.GetStringAsync("/api/products/1"));

        Assert.True(json.RootElement.TryGetProperty(champ, out _),
            $"Le contrat JSON du produit doit exposer '{champ}' (consommé par Ordering et Web).");
    }
}
