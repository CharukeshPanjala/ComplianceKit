module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'gateway',
        'policy',
        'docgen',
        'dsar',
        'common',
        'frontend',
        'infra',
        'ci',
        'deps',
        'release',
      ],
    ],
    'subject-case': [2, 'always', 'lower-case'],
  },
}