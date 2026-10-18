using System.Text.Json.Serialization;

namespace ECommerce.Catalog.Api.Models;

public class Product
{
    public int Id { get; set; }
    public required string Sku { get; set; }          // business reference, unique
    public required string Name { get; set; }
    public string? Description { get; set; }
    public decimal Price { get; set; }
    public int AvailableStock { get; set; }

    // Many-to-one relationship with Category.
    public int CategoryId { get; set; }
    [JsonIgnore]                                       // the API exposes CategoryId only
    public Category? Category { get; set; }
}
