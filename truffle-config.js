module.exports = {
  networks: {
    // Development network (Ganache)
    development: {
      host: "127.0.0.1",     // Localhost
      port: 7545,            // Standard Ganache GUI port (use 8545 for ganache-cli)
      network_id: "*",       // Match any network id
      gas: 6721975,          // Gas limit
      gasPrice: 20000000000  // 20 gwei
    },
    
    // Alternative Ganache CLI configuration
    ganache: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
      gas: 6721975,
      gasPrice: 20000000000
    }
  },

  // Configure your compilers
  compilers: {
    solc: {
      version: "0.8.20",      // Fetch exact version from solc-bin
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        },
        evmVersion: "paris"   // EVM version
      }
    }
  },

  // Truffle DB is currently disabled by default
  db: {
    enabled: false
  },

  // Configure mocha for tests
  mocha: {
    timeout: 100000
  },

  // Contracts directory
  contracts_directory: './contracts',
  contracts_build_directory: './build/contracts',
  migrations_directory: './migrations',
  test_directory: './test'
};
