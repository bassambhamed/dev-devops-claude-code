// Tests d'intégration de la création de commande (Ordering.Api).
//
// Le test du total est le filet qui aurait dû exister AVANT l'incident du lab 11 :
// une commande de 2 moniteurs doit coûter 2 x 329,00. C'est un comportement métier,
// pas un détail d'implémentation — exactement ce qu'un test doit figer.
using System.Diagnostics.Metrics;
using System.Net;
using System.Net.Http.Json;
using ECommerce.Ordering.Api.Diagnostics;
using Xunit;

namespace ECommerce.Ordering.Tests;

public class OrderingEndpointsTests(OrderingApiFactory factory) : IClassFixture<OrderingApiFactory>
{
    private readonly HttpClient _client = factory.CreateClient();

    private sealed record OrderResult(int Id, string Status, decimal Total);

    [Fact]
    public async Task CreateOrder_QuantitesMultiples_TotalEgalPrixFoisQuantite()
    {
        var commande = new { Customer = "Client Test", Items = new[] { new { ProductId = 3, Quantity = 2 }, new { ProductId = 1, Quantity = 1 } } };

        var response = await _client.PostAsJsonAsync("/api/orders", commande);

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        var order = await response.Content.ReadFromJsonAsync<OrderResult>();
        Assert.Equal("Confirmed", order!.Status);
        Assert.Equal(2 * 329.00m + 119.99m, order.Total);
    }

    [Fact]
    public async Task CreateOrder_SansLigne_Retourne400()
    {
        var response = await _client.PostAsJsonAsync("/api/orders", new { Customer = "Client Test", Items = Array.Empty<object>() });

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task CreateOrder_QuantiteNulleOuNegative_Retourne400()
    {
        var commande = new { Customer = "Client Test", Items = new[] { new { ProductId = 1, Quantity = 0 } } };

        var response = await _client.PostAsJsonAsync("/api/orders", commande);

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task CreateOrder_ProduitInconnu_Retourne400()
    {
        var commande = new { Customer = "Client Test", Items = new[] { new { ProductId = 999, Quantity = 1 } } };

        var response = await _client.PostAsJsonAsync("/api/orders", commande);

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task CreateOrder_Confirmee_IncrementeLaMetriqueOrdersCreated()
    {
        // On écoute la métrique métier comme le ferait un collecteur OpenTelemetry.
        long creees = 0;
        using var listener = new MeterListener();
        listener.InstrumentPublished = (instrument, l) =>
        {
            if (instrument.Meter.Name == OrderingTelemetry.Name && instrument.Name == "ecommerce.orders.created")
                l.EnableMeasurementEvents(instrument);
        };
        listener.SetMeasurementEventCallback<long>((_, value, _, _) => Interlocked.Add(ref creees, value));
        listener.Start();

        var commande = new { Customer = "Client Test", Items = new[] { new { ProductId = 1, Quantity = 1 } } };
        var response = await _client.PostAsJsonAsync("/api/orders", commande);

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        Assert.True(Interlocked.Read(ref creees) >= 1);
    }
}
