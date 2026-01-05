# FastMCP 2.13: Storage, Security, and Scale

When we [shipped](https://www.google.com/url?sa=E&q=https%3A%2F%2Fwww.jlowin.dev%2Fblog%2Ffastmcp-2-12) FastMCP 2.12 with its new [OAuth proxy](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fservers%2Fauth%2Foauth-proxy) on August 31st, something remarkable happened. Downloads exploded from 200,000 to a peak of **1.25 million a day**. The proxy, which bridges MCP’s modern DCR requirement with enterprise identity providers like Google and Azure, clearly hit a nerve. In fact, last week FastMCP surpassed the official MCP SDK in GitHub stars, a validation of the community’s demand for high-level, production-ready tooling.

With that kind of scale, you get a lot of feedback, fast.

This is the world **FastMCP 2.13** was built for. It is one of our largest releases, focused entirely on the infrastructure required for production MCP servers: persistent storage, battle-tested security, and performance optimizations.

Star FastMCP on GitHub or check out the updated docs at [gofastmcp.com](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com).

Battle-Tested Authentication

The massive adoption of the OAuth proxy meant the community immediately started battle-testing our auth implementation in real-world scenarios. We learned our original Azure provider only worked in the narrowest of cases; intrepid users helped us build a far more robust version. Others contributed a variety of new providers, with the result being that FastMCP now supports out-of-the-box authentication with:

1 [WorkOS](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com) and [AuthKit](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

2 [GitHub](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

3 [Google](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

4 [Azure](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit) (Entra ID)

5 [AWS Cognito](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

6 [Auth0](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

7 [Descope](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

8 [Scalekit](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

9 [JWTs](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

10 [RFC 7662 token introspection](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgofastmcp.com%2Fintegrations%2Fauthkit)

And we’re working with Supabase to add support for their new identity provider.

More critically, I owe a huge thanks to MCP Core Committee member Den Delimarsky for responsibly disclosing two nuanced, MCP-specific vulnerabilities: a confused deputy attack and a related token security boundary issue. The fixes required some novel solutions, including having the proxy issue its own tokens and implementing a new consent screen for explicit client approval. Our OAuth implementation is now hardened, spec-compliant, and thanks to the community’s scrutiny, ready for production.

You can learn more about confused deputy attacks from an [excellent post](https://www.google.com/url?sa=E&q=https%3A%2F%2Fden.dev%2Fblog%2Fmcp-confused-deputy-api-management%2F) on Den’s blog, and I’ll write a post on FastMCP’s specific implementation soon.

First-Class State Management

The rapid evolution of our auth stack highlighted a critical need: a robust way to manage persistent state. OAuth proxies need to store encrypted tokens and session data to survive restarts and work in distributed deployments.

To solve this, FastMCP maintainer Bill Easton built [py-key-value](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2Fstrawgate%2Fpy-key-value). This fantastic library is something I’ve long wished for in the Python ecosystem: a clean key-value store with portable backend support. Its real genius is the composable wrapper system that lets you layer encryption, TTLs, and caching onto _any_ backend, from a local filesystem to Redis or Elasticsearch.

It’s so good, we’ve baked it into FastMCP’s core. In 2.13, persistent storage is now built-in and enabled by default where appropriate, providing the foundation for stateful, production-ready MCP applications.

A Raft of Other Improvements

Beyond the headlines, this release is packed with features and fixes that came directly from community feedback:

1 **Response Caching:** The new ResponseCachingMiddleware provides an instant performance win for expensive, repeated tool and resource calls.

2 **Server Lifespans:** We fixed a long-standing point of confusion in the MCP SDK. lifespan now correctly refers to the _server_ lifecycle (for things like DB connections), not the client session. This is a breaking change, but it’s the correct one.

3 **Pydantic Validation:** We now use Pydantic for input validation, avoiding the SDK’s overly-strict JSON Schema enforcement. This more flexible approach is familiar to Python developers and more forgiving of LLMs that might send an integer as a string.

4 **Richer Context:** The Context API has been expanded, allowing your tools and resources to interact with other MCP functionality from inside their own execution.

What’s Next

FastMCP 2.13 marks the framework’s evolution into a production-ready platform. It includes work from **20 new contributors**, and it’s their production feedback that made these improvements possible. Thank you.

Looking ahead, our next major release, FastMCP 2.14, will be our first to remove deprecated features since launching 2.0. This is a sign of maturity: we’re cleaning up the API and solidifying the foundation for the long term.

Happy engineering!