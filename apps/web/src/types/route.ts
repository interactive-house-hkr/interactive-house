export async function GET() {
  try {
    const res = await fetch(
      "https://knolly-svetlana-beribboned.ngrok-free.dev/api/v1/devices",
      {
        method: "GET",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "ngrok-skip-browser-warning": "true",
        },
      }
    );

    if (!res.ok) {
      const text = await res.text();

      return Response.json(
        {
          error: "Failed to fetch devices from upstream",
          status: res.status,
          body: text,
        },
        { status: res.status }
      );
    }

    const data = await res.json();
    return Response.json(data, { status: 200 });
  } catch (error) {
    return Response.json(
      {
        error: "Server error",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}