#version 130

in vec3 FragPos;
in vec3 Color;
in vec3 Normal;

out vec4 outColor;

uniform vec3 viewPos;
uniform vec3 lightPos;
uniform vec3 lightColor;

void main()
{
    float ambientStrength = 0.2f;
    vec3 ambient = ambientStrength * lightColor;

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    float specularStrength = 0.5f;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16);
    vec3 specular = specularStrength * spec * lightColor;

    vec3 result = (ambient + diffuse + specular) * Color;
    outColor = vec4(result, 1.0f);
}
