using System.Text.Json.Serialization;

namespace ECommerce.Catalog.Api.Models;

public class Category
{
    public int Id { get; set; }
    public required string Name { get; set; }

    // One-to-many: a category groups several products.
    // Ignored in JSON to avoid serializing the whole catalog with each category.
    [JsonIgnore]
    public List<Product> Products { get; set; } = [];
}
