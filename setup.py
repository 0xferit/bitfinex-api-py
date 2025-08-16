from setuptools import setup

setup(
    name="bitfinex-api-py-postonly",
    version="3.0.5.post1",
    description="Bitfinex Python API with enforced POST_ONLY orders - prevents accidental market/taker orders",
    long_description=(
        "A safety-enhanced fork of the official Bitfinex Python API that "
        "enforces POST_ONLY (maker-only) flag on ALL orders. "
        "Prevents accidental market orders, taker fees, and costly trading mistakes. "
        "Orders will never cross the spread. Perfect for market makers, grid bots, and safety-critical trading. "
        "Drop-in replacement for bitfinex-api-py with automatic POST_ONLY enforcement."
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/0xferit/bitfinex-api-py",
    author="0xferit",
    author_email="ferit@example.com",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="bitfinex,api,trading,post-only,postonly,maker-only,maker,safety,no-taker,bitcoin,cryptocurrency,exchange,limit-order,market-maker,grid-trading,algo-trading",
    project_urls={
        "Original Source": "https://github.com/bitfinexcom/bitfinex-api-py",
        "Fork Source": "https://github.com/0xferit/bitfinex-api-py",
        "Documentation": "https://github.com/0xferit/bitfinex-api-py/blob/master/README.md",
        "Issues": "https://github.com/0xferit/bitfinex-api-py/issues",
    },
    packages=[
        "bfxapi",
        "bfxapi._utils",
        "bfxapi.constants",  # CRITICAL: Added for POST_ONLY flag
        "bfxapi.types",
        "bfxapi.websocket",
        "bfxapi.websocket._client",
        "bfxapi.websocket._handlers",
        "bfxapi.websocket._event_emitter",
        "bfxapi.rest",
        "bfxapi.rest._interface",
        "bfxapi.rest._interfaces",
    ],
    install_requires=[
        "pyee~=11.1.0",
        "websockets~=12.0",
        "requests~=2.32.3",
    ],
    extras_require={
        "typing": [
            "types-requests~=2.32.0.20241016",
        ]
    },
    python_requires=">=3.8",
    package_data={"bfxapi": ["py.typed"]},
)
